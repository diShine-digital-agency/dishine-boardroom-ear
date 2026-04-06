import os
import logging
from anthropic import Anthropic
from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
_DEFAULT_MAX_TOKENS = 2048

_PROMPT_TEMPLATE = """
You are a top-tier executive consultant.
Analyze the following boardroom transcript (anonymized for NDA compliance) and provide a professional "Strategic Action Plan".

Structure your response as follows:
1. **Executive Summary**: A high-level overview of the discussion.
2. **Key Strategic Objectives**: What are the main goals discussed?
3. **Identified Risks**: Any potential roadblocks or legal/financial concerns.
4. **Action Items**: A bulleted list of next steps with prioritized owners.
5. **Confidentiality Note**: A reminder of the NDA-compliant nature of this analysis.

Do not invent facts, hallucinate, or extrapolate information. Every statement must be directly traceable to the transcript below.

Transcript:
\"\"\"{transcript}\"\"\"
"""


class StrategicPlanner:
    """Generates a structured executive action plan from an anonymised transcript.

    Parameters
    ----------
    api_key : str or None
        Anthropic API key. Falls back to the ``ANTHROPIC_API_KEY`` environment
        variable if not provided.
    model : str
        Claude model identifier (default: ``claude-3-5-sonnet-20241022``).
    max_tokens : int
        Maximum tokens in the generated plan.
    """

    def __init__(self, api_key=None, model=_DEFAULT_MODEL, max_tokens=_DEFAULT_MAX_TOKENS):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.max_tokens = max_tokens

        if self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
            except Exception as exc:
                logger.warning("Failed to initialise Anthropic client: %s", exc)
                self.client = None
        else:
            self.client = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_plan(self, transcript_text: str) -> str | None:
        """Generate a strategic action plan from *transcript_text*.

        Parameters
        ----------
        transcript_text : str
            Anonymised transcript content.

        Returns
        -------
        str or None
            Markdown-formatted action plan, or ``None`` if unavailable.
        """
        if not self.client:
            console.print(
                "[bold yellow]Warning:[/bold yellow] Anthropic API key not set. "
                "Strategic plan generation skipped."
            )
            logger.warning("StrategicPlanner: no API key — plan generation skipped.")
            return None

        if not transcript_text or not transcript_text.strip():
            logger.warning("StrategicPlanner: received empty transcript — skipping.")
            console.print(
                "[bold yellow]Warning:[/bold yellow] Transcript is empty. "
                "Strategic plan generation skipped."
            )
            return None

        console.print("[bold cyan]![/bold cyan] Generating Strategic Action Plan via Claude...")
        logger.info("Calling Anthropic API (model=%s).", self.model)

        prompt = _PROMPT_TEMPLATE.format(transcript=transcript_text)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            plan = message.content[0].text
            logger.info("Strategic plan generated successfully (%d chars).", len(plan))
            return plan

        except Exception as exc:
            logger.exception("Anthropic API call failed.")
            console.print(f"[bold red]Error calling Anthropic API:[/bold red] {exc}")
            return None


if __name__ == "__main__":
    # Smoke-test (requires a valid key in ANTHROPIC_API_KEY env var)
    planner = StrategicPlanner()
    result = planner.generate_plan("Discussion about expanding into new markets in Q3.")
    if result:
        print(result)
    else:
        print("No plan generated (check your API key).")
