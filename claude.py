from anthropic import Anthropic
import os

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# async def ask_claude(prompt: str) -> str:
#     response = client.messages.create(
#         model="claude-3-haiku-20240307",
#         max_tokens=300,
#         messages=[{"role": "user", "content": prompt}]
#     )
#     return response.content[0].text

    # return "Claude is not configured yet."

async def ask_claude(prompt: str) -> str:
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"Claude error: {str(e)}"