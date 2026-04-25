import os
import sys
import argparse
import logging
import logging.config
import yaml

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Heavy imports (faster_whisper, anthropic) are deferred into the call sites
# that actually need them, so ``--help`` and ``--health-check`` work before
# the full dependency set is installed.

__version__ = "1.3.0"

console = Console()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _setup_logging(log_level: str = "INFO", log_file: str | None = None) -> None:
    """Configure logging from logging.yaml when present, otherwise apply defaults."""
    yaml_path = os.path.join(os.path.dirname(__file__), "logging.yaml")
    if os.path.exists(yaml_path):
        with open(yaml_path, "r") as fh:
            cfg = yaml.safe_load(fh)
        logging.config.dictConfig(cfg)
        return

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if log_file:
        os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_DEFAULTS = {
    "model_size": "small",
    "device": "auto",
    "compute_type": "float32",
    "anthropic_api_key": "",
    "auto_anonymize": True,
    "output_format": "markdown",
    "output_dir": "transcripts",
    "drop_dir": "drop_here",
    "anonymization_level": "basic",
    "log_level": "INFO",
    "log_file": None,
    "audit_log": "transcripts/audit.log",
    "timeout": 3600,
}


def load_config(config_path: str = "config.yaml") -> dict:
    """Load YAML config, apply .env overrides, and fill defaults."""
    load_dotenv()

    config = dict(_DEFAULTS)

    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as fh:
                yaml_cfg = yaml.safe_load(fh) or {}
            config.update({k: v for k, v in yaml_cfg.items() if v is not None})
        except Exception as exc:
            console.print(f"[bold yellow]Warning:[/bold yellow] Could not read {config_path}: {exc}")

    # Environment variables take precedence over config.yaml
    env_map = {
        "ANTHROPIC_API_KEY": "anthropic_api_key",
        "BOARDROOM_MODEL_SIZE": "model_size",
        "BOARDROOM_DEVICE": "device",
        "BOARDROOM_COMPUTE_TYPE": "compute_type",
        "BOARDROOM_OUTPUT_DIR": "output_dir",
        "BOARDROOM_LOG_LEVEL": "log_level",
        "BOARDROOM_LOG_FILE": "log_file",
        "BOARDROOM_AUDIT_LOG": "audit_log",
    }
    for env_key, cfg_key in env_map.items():
        val = os.getenv(env_key)
        if val:
            config[cfg_key] = val

    return config


def validate_config(config: dict) -> None:
    """Raise ValueError for clearly invalid configuration values."""
    from core.boardroom_ear import VALID_MODEL_SIZES, VALID_DEVICES, VALID_COMPUTE_TYPES

    ms = config.get("model_size", "")
    if ms not in VALID_MODEL_SIZES:
        raise ValueError(
            f"Invalid model_size '{ms}' in config. "
            f"Choose from: {', '.join(sorted(VALID_MODEL_SIZES))}"
        )

    dev = config.get("device", "")
    if dev not in VALID_DEVICES:
        raise ValueError(
            f"Invalid device '{dev}' in config. "
            f"Choose from: {', '.join(sorted(VALID_DEVICES))}"
        )

    ct = config.get("compute_type", "")
    if ct not in VALID_COMPUTE_TYPES:
        raise ValueError(
            f"Invalid compute_type '{ct}' in config. "
            f"Choose from: {', '.join(sorted(VALID_COMPUTE_TYPES))}"
        )


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="boardroom-ear",
        description="diShine Boardroom Ear — NDA-compliant local transcriber & strategic analyser.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python Boardroom_Ear.py\n"
            "  python Boardroom_Ear.py --model small --input meeting.mp3\n"
            "  python Boardroom_Ear.py --batch --input-dir drop_here/ --output-dir transcripts/\n"
            "  python Boardroom_Ear.py --anonymization full --dry-run\n"
        ),
    )

    parser.add_argument(
        "--model",
        dest="model_size",
        choices=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"],
        help="Whisper model size (overrides config.yaml).",
    )
    parser.add_argument(
        "--device",
        choices=["cpu", "cuda", "auto"],
        help="Compute device (overrides config.yaml). CTranslate2 has no Metal/MPS backend, so Apple Silicon resolves to 'cpu' via 'auto'.",
    )
    parser.add_argument(
        "--compute-type",
        dest="compute_type",
        choices=["int8", "float16", "float32", "int8_float16"],
        help="CTranslate2 compute precision (overrides config.yaml).",
    )
    parser.add_argument(
        "--input",
        dest="input_file",
        metavar="FILE",
        help="Process a specific audio file instead of scanning drop_here/.",
    )
    parser.add_argument(
        "--input-dir",
        dest="input_dir",
        metavar="DIR",
        help="Directory to scan for audio files (batch mode).",
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        metavar="DIR",
        help="Output directory for transcripts (default: transcripts/).",
    )
    parser.add_argument(
        "--anonymization",
        dest="anonymization_level",
        choices=["none", "basic", "full"],
        default=None,
        help=(
            "PII scrubbing level: none = raw text, basic = token placeholders (default), "
            "full = blank redaction."
        ),
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process all supported audio files found in the input directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate setup and print what would be processed without transcribing.",
    )
    parser.add_argument(
        "--no-plan",
        action="store_true",
        help="Skip Strategic Action Plan generation even if an API key is configured.",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=None,
        help="Logging verbosity (default: INFO).",
    )
    parser.add_argument(
        "--config",
        dest="config_path",
        default="config.yaml",
        metavar="FILE",
        help="Path to config.yaml (default: config.yaml).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        metavar="SECONDS",
        help="Maximum transcription time in seconds (default: 3600).",
    )

    return parser


# ---------------------------------------------------------------------------
# Processing helpers
# ---------------------------------------------------------------------------

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".ogg", ".flac", ".aac"}


def discover_audio_files(directory: str) -> list[str]:
    if not os.path.isdir(directory):
        return []
    return sorted(
        [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS
        ],
        key=os.path.getmtime,
        reverse=True,
    )


def process_file(
    audio_path: str,
    ear,  # core.boardroom_ear.BoardroomEar — untyped to keep this import lazy
    config: dict,
    dry_run: bool = False,
    no_plan: bool = False,
) -> None:
    logger = logging.getLogger(__name__)
    # Deferred — scrubber is cheap, StrategicPlanner pulls in the anthropic SDK.
    from analysis.scrubber import PII_Scrubber
    from analysis.strategic_planner import StrategicPlanner

    # Transcribe
    transcript = ear.transcribe(audio_path, output_dir=config["output_dir"], dry_run=dry_run)

    if dry_run:
        return

    # Anonymise
    anon_level = config.get("anonymization_level", "basic")
    api_key = config.get("anthropic_api_key", "")

    if not api_key and not no_plan:
        api_key = Prompt.ask(
            "[bold yellow]?[/bold yellow] Anthropic API Key "
            "[dim](leave blank to skip Strategic Plan)[/dim]",
            password=True,
            default="",
        )

    if api_key and not no_plan:
        if anon_level != "none":
            redaction_mode = "blank" if anon_level == "full" else "token"
            scrubber = PII_Scrubber(
                audit_log_path=config.get("audit_log"),
                redaction_mode=redaction_mode,
            )
            console.print("[bold cyan]![/bold cyan] Anonymising transcript for NDA compliance...")
            anonymized_text = scrubber.scrub(transcript)
            logger.info("Transcript anonymised (level=%s).", anon_level)
        else:
            anonymized_text = transcript
            logger.info("Anonymisation skipped (level=none).")

        planner = StrategicPlanner(api_key=api_key)
        plan = planner.generate_plan(anonymized_text)

        if plan:
            basename = os.path.splitext(os.path.basename(audio_path))[0]
            plan_file = os.path.join(
                config["output_dir"], f"{basename}_StrategicPlan.md"
            )
            os.makedirs(config["output_dir"], exist_ok=True)
            try:
                with open(plan_file, "w", encoding="utf-8") as fh:
                    fh.write(f"# Strategic Action Plan — diShine\n\n{plan}")
                console.print(
                    f"[bold green]✔[/bold green] Strategic Plan saved to: "
                    f"[bold underline]{plan_file}[/bold underline]"
                )
                logger.info("Strategic plan saved to %s", plan_file)
            except OSError as exc:
                console.print(f"[bold red]Error:[/bold red] Could not save plan: {exc}")
                logger.error("Failed to save strategic plan: %s", exc)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def health_check(config: dict) -> None:
    """Print a diagnostics summary and exit."""
    import importlib.util  # submodule must be imported explicitly (Python 3.12+)

    console.print(Panel("[bold cyan]diShine Boardroom Ear — Health Check[/bold cyan]", expand=False))

    checks = {
        "Python ≥ 3.9": sys.version_info >= (3, 9),
        "faster-whisper installed": bool(importlib.util.find_spec("faster_whisper")),
        "anthropic installed": bool(importlib.util.find_spec("anthropic")),
        "rich installed": bool(importlib.util.find_spec("rich")),
        "PyYAML installed": bool(importlib.util.find_spec("yaml")),
        "python-dotenv installed": bool(importlib.util.find_spec("dotenv")),
        "config.yaml present": os.path.exists("config.yaml"),
        "drop_here/ accessible": os.path.isdir(config.get("drop_dir", "drop_here")),
    }

    all_ok = True
    for label, status in checks.items():
        icon = "[bold green]✔[/bold green]" if status else "[bold red]✗[/bold red]"
        console.print(f"  {icon} {label}")
        if not status:
            all_ok = False

    if all_ok:
        console.print("\n[bold green]All checks passed. Ready to run.[/bold green]")
    else:
        console.print("\n[bold yellow]Some checks failed. See TROUBLESHOOTING.md for guidance.[/bold yellow]")

    sys.exit(0 if all_ok else 1)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    # Insert hidden --health-check flag
    parser.add_argument("--health-check", action="store_true", help=argparse.SUPPRESS)

    args = parser.parse_args(argv)

    config = load_config(args.config_path)

    # CLI overrides
    if args.model_size:
        config["model_size"] = args.model_size
    if args.device:
        config["device"] = args.device
    if args.compute_type:
        config["compute_type"] = args.compute_type
    if args.output_dir:
        config["output_dir"] = args.output_dir
    if args.anonymization_level:
        config["anonymization_level"] = args.anonymization_level
    if args.log_level:
        config["log_level"] = args.log_level
    if args.timeout is not None:
        config["timeout"] = args.timeout

    _setup_logging(
        log_level=config.get("log_level", "INFO"),
        log_file=config.get("log_file"),
    )
    logger = logging.getLogger(__name__)

    # Health check shortcut
    if args.health_check:
        health_check(config)

    # Validate config
    try:
        validate_config(config)
    except ValueError as exc:
        console.print(f"[bold red]Configuration error:[/bold red] {exc}")
        sys.exit(1)

    console.print(
        Panel(
            f"[bold cyan]diShine Boardroom Ear v{__version__}[/bold cyan]\n"
            "[dim]100% NDA-compliant local transcriber[/dim]",
            expand=False,
        )
    )

    # Ensure required directories exist
    drop_dir = config.get("drop_dir", "drop_here")
    os.makedirs(drop_dir, exist_ok=True)
    os.makedirs(config.get("output_dir", "transcripts"), exist_ok=True)

    # Determine files to process
    if args.input_file:
        audio_files = [args.input_file]
    elif args.batch or args.input_dir:
        scan_dir = args.input_dir or drop_dir
        audio_files = discover_audio_files(scan_dir)
        if not audio_files:
            console.print(
                f"[bold yellow]![/bold yellow] No supported audio files found in [bold]{scan_dir}[/bold]."
            )
            sys.exit(0)
        console.print(
            f"[bold green]✔[/bold green] Found {len(audio_files)} file(s) to process."
        )
    else:
        audio_files = discover_audio_files(drop_dir)
        if not audio_files:
            console.print(
                f"[bold yellow]![/bold yellow] No audio files found in [bold]{drop_dir}/[/bold].\n"
                "Drop a .mp3 / .wav / .m4a file in that folder and run again, or use --input FILE."
            )
            sys.exit(0)
        # Default: process only the most-recently-modified file
        audio_files = [audio_files[0]]

    # Initialise transcription engine once (model shared across batch).
    # Import is deferred so --help / --health-check do not require faster-whisper.
    from core.boardroom_ear import BoardroomEar

    ear = BoardroomEar(
        model_size=config["model_size"],
        device=config["device"],
        compute_type=config["compute_type"],
        timeout=int(config.get("timeout", 3600)),
    )

    for audio_path in audio_files:
        console.print(f"\n[bold]Processing:[/bold] {os.path.basename(audio_path)}")
        logger.info("Processing file: %s", audio_path)
        try:
            process_file(
                audio_path=audio_path,
                ear=ear,
                config=config,
                dry_run=args.dry_run,
                no_plan=args.no_plan,
            )
        except (FileNotFoundError, ValueError) as exc:
            console.print(f"[bold red]Error:[/bold red] {exc}")
            logger.error("Skipping %s: %s", audio_path, exc)
            if not args.batch:
                sys.exit(1)
        except Exception as exc:
            console.print(f"[bold red]Unexpected error:[/bold red] {exc}")
            logger.exception("Unexpected error processing %s", audio_path)
            if not args.batch:
                sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Cancelled by user.[/bold red]")
    except Exception as exc:
        console.print(f"\n[bold red]Fatal Error:[/bold red] {exc}")
        sys.exit(1)
