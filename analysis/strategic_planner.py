import os
from anthropic import Anthropic
from rich.console import Console

console = Console()

class StrategicPlanner:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.client = Anthropic(api_key=self.api_key)
        else:
            self.client = None

    def generate_plan(self, transcript_text):
        if not self.client:
            console.print("[bold yellow]Warning:[/bold yellow] Anthropic API Key not found. Plan generation skipped.")
            return None

        console.print("[bold cyan]![/bold cyan] Generating Strategic Action Plan via Claude...")
        
        prompt = f"""
        You are a top-tier executive consultant.
        Analyze the following boardroom transcript (anonymized for NDA compliance) and provide a professional "Strategic Action Plan".
        
        Structure your response as follows:
        1. **Executive Summary**: A high-level overview of the discussion.
        2. **Key Strategic Objectives**: What are the main goals discussed?
        3. **Identified Risks**: Any potential roadblocks or legal/financial concerns.
        4. **Action Items**: A bulleted list of next steps with prioritized owners.
        5. **Confidentiality Note**: A reminder of the NDA-compliant nature of this analysis.

        Avoid at all costs invented facts, halucintations and extrapolated informations. All informtions provided in you plan should be verifiable.
        
        Transcript:
        \"\"\"{transcript_text}\"\"\"
        """
        
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            console.print(f"[bold red]Error calling Anthropic API:[/bold red] {e}")
            return None

if __name__ == "__main__":
    # Test with dummy data
    planner = StrategicPlanner("dummy_key")
    # This will fail unless key is valid, but good for structure test
    # print(planner.generate_plan("Test transcript content."))
