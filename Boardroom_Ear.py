import os
import sys
import yaml
from core.boardroom_ear import BoardroomEar
from analysis.scrubber import PII_Scrubber
from analysis.strategic_planner import StrategicPlanner
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

def load_config():
    config_path = "config.yaml"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {
        "model_size": "small",
        "device": "auto",
        "compute_type": "float32",
        "anthropic_api_key": ""
    }

def main():
    console.print(Panel("[bold cyan]diShine Boardroom Ear v1.0[/bold cyan]\n[dim]100% NDA-Compliant Local Transcriber[/dim]", expand=False))
    
    config = load_config()
    
    # 1. Select Audio
    drop_dir = "drop_here"
    if not os.path.exists(drop_dir):
        os.makedirs(drop_dir)
        
    files = [f for f in os.listdir(drop_dir) if f.endswith(('.mp3', '.wav', '.m4a', '.mp4'))]
    
    if not files:
        console.print(f"[bold yellow]![/bold yellow] No audio files found in [bold]{drop_dir}/[/bold].")
        console.print("Please drop an audio file (.mp3, .wav) in the folder and run again.")
        return

    # In a real tool, we might pick the latest or let user choose. Let's pick the latest.
    files.sort(key=lambda x: os.path.getmtime(os.path.join(drop_dir, x)), reverse=True)
    audio_file = os.path.join(drop_dir, files[0])
    
    console.print(f"[bold green]✔[/bold green] Found audio: [bold cyan]{files[0]}[/bold cyan]")

    # 2. Transcription
    ear = BoardroomEar(
        model_size=config.get("model_size", "small"),
        device=config.get("device", "auto"),
        compute_type=config.get("compute_type", "float32")
    )
    
    transcript = ear.transcribe(audio_file)
    
    # 3. Optional Strategic Analysis
    api_key = config.get("anthropic_api_key")
    if not api_key:
        api_key = Prompt.ask("[bold yellow]?[/bold yellow] Anthropic API Key [dim](leave blank to skip Strategic Plan)[/dim]", password=True)
        
    if api_key:
        # Scrub first
        scrubber = PII_Scrubber()
        console.print("[bold cyan]![/bold cyan] Anonymizing transcript for NDA compliance...")
        anonymized_text = scrubber.scrub(transcript)
        
        # Plan
        planner = StrategicPlanner(api_key=api_key)
        plan = planner.generate_plan(anonymized_text)
        
        if plan:
            # Save plan
            plan_file = os.path.join("transcripts", f"{os.path.splitext(files[0])[0]}_StrategicPlan.md")
            with open(plan_file, "w") as f:
                f.write(f"# Strategic Action Plan - diShine\n\n{plan}")
            console.print(f"[bold green]✔[/bold green] Strategic Plan saved to: [bold underline]{plan_file}[/bold underline]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Cancelled by user.[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]Fatal Error:[/bold red] {e}")
