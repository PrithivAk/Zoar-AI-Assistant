"""
Thin wrapper so the rest of the app doesn't care whether we're calling
Groq or OpenAI. Both APIs are OpenAI-compatible, so this is ~20 lines.
"""
import os
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")


def _get_client():
    if PROVIDER == "groq":
        from groq import Groq
        return Groq(api_key=os.getenv("GROQ_API_KEY"))
    elif PROVIDER == "openai":
        from openai import OpenAI
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {PROVIDER}")


_client = None


def chat(system_prompt: str, user_message: str, history: list | None = None) -> str:
    """
    Send a single-turn (or short multi-turn) chat request.
    history: optional list of {"role": "user"/"assistant", "content": str}
    Returns the assistant's text reply.
    """
    global _client
    if _client is None:
        _client = _get_client()

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    response = _client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()
