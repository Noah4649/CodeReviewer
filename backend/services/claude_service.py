import json
import os
import anthropic
from dotenv import load_dotenv
from backend.models.schemas import ReviewResponse
from backend.services.prompt import SYSTEM_PROMPT, build_user_message

load_dotenv()

# Initialise the Anthropic client once at import time
_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1500

FALLBACK_SECTION = "Unable to generate feedback for this section. Please try again."


def get_review(language: str, code: str, user_prompt: str | None) -> ReviewResponse:
    """
    Send code to Claude and return structured feedback.
    Raises ValueError if the response cannot be parsed.
    Raises anthropic.APIError on API-level failures (caught in the router).
    """
    user_message = build_user_message(language, code, user_prompt)

    message = _client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_text = message.content[0].text.strip()

    # Strip markdown fences if Claude wraps the JSON despite instructions
    if raw_text.startswith("```"):
        lines = raw_text.splitlines()
        raw_text = "\n".join(
            line for line in lines if not line.startswith("```")
        ).strip()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude returned non-JSON response: {e}") from e

    return ReviewResponse(
        bugs=data.get("bugs", FALLBACK_SECTION),
        security=data.get("security", FALLBACK_SECTION),
        concepts=data.get("concepts", FALLBACK_SECTION),
    )