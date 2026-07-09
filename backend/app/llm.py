import os
import httpx
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openrouter/free"


async def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    """
    Sends a chat completion request to OpenRouter and returns the text response.
    Used by every agent (Planner, Code Generator, Reviewer, Debugger) —
    each just passes a different system_prompt to control its behavior.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]