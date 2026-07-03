"""
Orchestrator = intent router. One LLM call classifies the user's message
into one of: wellness, shopping, interview, general.
"""
from llm_client import chat

ROUTER_SYSTEM_PROMPT = """You are an intent router for a personal AI assistant called Zoar.
Given a user's message, classify it into EXACTLY ONE of these categories:

- wellness: mood check-ins, feelings, stress, anxiety, journaling
- shopping: product searches, recommendations, "I need to buy X"
- interview: mock interview practice, career prep, interview questions
- general: anything else (greetings, small talk, unclear intent)

Respond with ONLY the category word, nothing else. No punctuation, no explanation.
"""

VALID_INTENTS = {"wellness", "shopping", "interview", "general"}


def route_intent(user_input: str) -> str:
    """Classify user input into an intent category."""
    result = chat(ROUTER_SYSTEM_PROMPT, user_input).strip().lower()
    # Guard against the model returning something unexpected
    for intent in VALID_INTENTS:
        if intent in result:
            return intent
    return "general"


if __name__ == "__main__":
    # Quick manual test — run: python orchestrator.py
    test_inputs = [
        "I'm feeling really anxious about tomorrow",
        "I need running shoes under 3000 rupees",
        "Can you ask me some HR interview questions?",
        "Hey what's up",
    ]
    for msg in test_inputs:
        print(f"{msg!r:55} -> {route_intent(msg)}")
