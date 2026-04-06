import os
import time
import sys
import logging
import signal
from faster_whisper import WhisperModel
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

console = Console()
logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".ogg", ".flac", ".aac"}
VALID_MODEL_SIZES = {"tiny", "base", "small", "medium", "large", "large-v2", "large-v3"}
VALID_DEVICES = {"cpu", "cuda", "mps", "auto"}
VALID_COMPUTE_TYPES = {"int8", "float16", "float32", "int8_float16"}

DEFAULT_TIMEOUT = 3600  # 1 hour


class TranscriptionTimeoutError(Exception):
    pass


class BoardroomEar:
    def __init__(self, model_size="base", device="cpu", compute_type="int8", timeout=DEFAULT_TIMEOUT):
        self.model_size = self._validate_model_size(model_size)
        self.device = self._validate_device(device)
        self.compute_type = self._validate_compute_type(compute_type)
        self.timeout = timeout
        self.model = None

    # --- Validation helpers ---

    def _validate_model_size(self, size):
        if size not in VALID_MODEL_SIZES:
            raise ValueError(
                f"Invalid model_size '{size}'. Choose from: {', '.join(sorted(VALID_MODEL_SIZES))}"
            )
        return size

    def _validate_device(self, device):
        if device not in VALID_DEVICES:
            raise ValueError(
                f"Invalid device '{device}'. Choose from: {', '.join(sorted(VALID_DEVICES))}"
            )
        return device

    def _validate_compute_type(self, compute_type):
        if compute_type not in VALID_COMPUTE_TYPES:
            raise ValueError(
                f"Invalid compute_type '{compute_type}'. Choose from: {', '.join(sorted(VALID_COMPUTE_TYPES))}"
            )
        return compute_type

    def _validate_audio_file(self, audio_path):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if not os.path.isfile(audio_path):
            raise ValueError(f"Path is not a file: {audio_path}")

        ext = os.path.splitext(audio_path)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported audio format '{ext}'. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )

        file_size = os.path.getsize(audio_path)
        if file_size == 0:
            raise ValueError(f"Audio file is empty (0 bytes): {audio_path}")

        if file_size < 512:
            raise ValueError(
                f"Audio file appears corrupted (only {file_size} bytes): {audio_path}"
            )

        logger.debug("Audio file validated: %s (%.2f MB)", audio_path, file_size / 1_048_576)

    def _ensure_output_dir(self, output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as exc:
            raise OSError(f"Cannot create output directory '{output_dir}': {exc}") from exc

        # Basic disk-space sanity check (warn if < 100 MB free)
        try:
            stat = os.statvfs(output_dir)
            free_mb = (stat.f_bavail * stat.f_frsize) / 1_048_576
            if free_mb < 100:
                logger.warning(
                    "Low disk space: %.0f MB free in '%s'. Transcripts may fail to save.",
                    free_mb,
                    output_dir,
                )
                console.print(
                    f"[bold yellow]⚠[/bold yellow] Low disk space: {free_mb:.0f} MB free. "
                    "Transcripts may not save correctly."
                )
        except AttributeError:
            # os.statvfs not available on Windows
            pass

    # --- Model loading ---

    def load_model(self):
        console.print(
            f"[bold cyan]![/bold cyan] Loading Local Whisper Model ([bold]{self.model_size}[/bold])..."
        )
        logger.info("Loading Whisper model: %s / device=%s / compute=%s",
                    self.model_size, self.device, self.compute_type)
        try:
            self.model = WhisperModel(
                self.model_size, device=self.device, compute_type=self.compute_type
            )
        except Exception as exc:
            logger.exception("Failed to load Whisper model.")
            raise RuntimeError(f"Failed to load Whisper model '{self.model_size}': {exc}") from exc

        console.print("[bold green]✔[/bold green] Model loaded successfully.")
        logger.info("Whisper model loaded successfully.")

    # --- Transcription ---

    def transcribe(self, audio_path, output_dir="transcripts", dry_run=False):
        self._validate_audio_file(audio_path)
        self._ensure_output_dir(output_dir)

        if not self.model:
            self.load_model()

        filename = os.path.basename(audio_path)
        name, _ = os.path.splitext(filename)
        output_file = os.path.join(output_dir, f"{name}_transcript.txt")

        console.print(f"[bold cyan]![/bold cyan] Transcribing: [dim]{filename}[/dim]")
        logger.info("Starting transcription: %s → %s", audio_path, output_file)

        if dry_run:
            console.print("[bold yellow]DRY-RUN:[/bold yellow] Skipping actual transcription.")
            logger.info("Dry-run mode: transcription skipped.")
            return ""

        # Timeout via SIGALRM (Unix only)
        _timeout_supported = hasattr(signal, "SIGALRM")
        if _timeout_supported and self.timeout:
            def _handle_timeout(signum, frame):
                raise TranscriptionTimeoutError(
                    f"Transcription exceeded timeout of {self.timeout}s. "
                    "Try a smaller model or shorter audio file."
                )
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(int(self.timeout))

        try:
            start_time = time.time()

            try:
                segments, info = self.model.transcribe(audio_path, beam_size=5)
            except Exception as exc:
                logger.exception("Whisper transcription call failed.")
                raise RuntimeError(
                    f"Transcription failed for '{filename}'. "
                    "The file may be corrupted or use an unsupported codec.\n"
                    f"Details: {exc}"
                ) from exc

            console.print(
                f"[bold blue]ℹ[/bold blue] Detected language: [bold]{info.language}[/bold] "
                f"(probability: {info.language_probability:.2f})"
            )
            logger.info("Detected language: %s (p=%.2f)", info.language, info.language_probability)

            full_text = []

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Transcribing...", total=info.duration)

                for segment in segments:
                    progress.update(task, completed=segment.end)
                    full_text.append(segment.text.strip())

            duration = time.time() - start_time

        finally:
            if _timeout_supported and self.timeout:
                signal.alarm(0)

        transcript_text = "\n".join(full_text)

        # Save to file
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(transcript_text)
        except OSError as exc:
            logger.exception("Failed to write transcript file.")
            raise OSError(f"Could not save transcript to '{output_file}': {exc}") from exc

        console.print(f"[bold green]✔[/bold green] Transcription complete in {duration:.2f}s.")
        console.print(
            f"[bold green]✔[/bold green] Saved to: [bold underline]{output_file}[/bold underline]"
        )
        logger.info("Transcription complete in %.2fs. Saved to %s", duration, output_file)

        return transcript_text


if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("[bold red]Error:[/bold red] Please provide an audio file path.")
        sys.exit(1)

    audio_file = sys.argv[1]
    ear = BoardroomEar()
    ear.transcribe(audio_file)
