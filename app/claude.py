from anthropic import Anthropic
import os

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
class ClaudeServiceError(Exception):
    def __init__(self, message: str, code: str = "AI_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


async def ask_claude(prompt: str) -> str:
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    except Exception as e:
        err_msg = str(e)

        if "credit balance is too low" in err_msg:
            raise ClaudeServiceError(
                "AI service quota exceeded. Please try again later.",
                code="QUOTA_EXCEEDED"
            )

        raise ClaudeServiceError(
            "AI service is temporarily unavailable.",
            code="AI_UNAVAILABLE"
        )