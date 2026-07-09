import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

MAX_RETRIES = 4
FALLBACK_DELAY_SECONDS = 10


async def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    """
    Sends a chat completion request to Groq and returns the text response.
    Groq's free tier has a dedicated per-account rate limit (not shared globally
    like OpenRouter's free pool), so it's faster and more predictable.
    Retries automatically if rate-limited, respecting Groq's Retry-After header.
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
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

    last_error = None
    for attempt in range(MAX_RETRIES):
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(GROQ_URL, headers=headers, json=payload)

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                wait_time = int(float(retry_after)) if retry_after else FALLBACK_DELAY_SECONDS
                print(f"Rate limited (429). Retrying in {wait_time}s... (attempt {attempt + 1}/{MAX_RETRIES})")
                last_error = httpx.HTTPStatusError(
                    "429 Too Many Requests", request=response.request, response=response
                )
                await asyncio.sleep(wait_time)
                continue

            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    raise last_error