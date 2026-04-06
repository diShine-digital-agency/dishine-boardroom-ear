import os
import time
import sys
from faster_whisper import WhisperModel
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

console = Console()

class BoardroomEar:
    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None

    def load_model(self):
        console.print(f"[bold cyan]![/bold cyan] Loading Local Whisper Model ([bold]{self.model_size}[/bold])...")
        self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        console.print("[bold green]✔[/bold green] Model loaded successfully.")

    def transcribe(self, audio_path, output_dir="transcripts"):
        if not self.model:
            self.load_model()

        filename = os.path.basename(audio_path)
        name, _ = os.path.splitext(filename)
        output_file = os.path.join(output_dir, f"{name}_transcript.txt")

        console.print(f"[bold cyan]![/bold cyan] Transcribing: [dim]{filename}[/dim]")
        
        start_time = time.time()
        
        # segments is a generator
        segments, info = self.model.transcribe(audio_path, beam_size=5)
        
        console.print(f"[bold blue]ℹ[/bold blue] Detected language: [bold]{info.language}[/bold] (probability: {info.language_probability:.2f})")
        
        full_text = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Transcribing...", total=info.duration)
            
            for segment in segments:
                # Update progress based on segment timing
                progress.update(task, completed=segment.end)
                full_text.append(segment.text)
                
        duration = time.time() - start_time
        
        # Save to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(full_text))

        console.print(f"[bold green]✔[/bold green] Transcription complete in {duration:.2f}s.")
        console.print(f"[bold green]✔[/bold green] Saved to: [bold underline]{output_file}[/bold underline]")
        
        return "\n".join(full_text)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("[bold red]Error:[/bold red] Please provide an audio file path.")
        sys.exit(1)
        
    audio_file = sys.argv[1]
    ear = BoardroomEar()
    ear.transcribe(audio_file)
