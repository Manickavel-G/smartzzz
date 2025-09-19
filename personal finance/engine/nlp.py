import os
from transformers import pipeline

USE_HF = os.getenv("USE_HF", "false").lower() == "true"

# Load HuggingFace zero-shot if enabled
hf_classifier = None
if USE_HF:
    hf_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

INTENTS = {
    "budget": ["budget", "summary", "spend", "expenses"],
    "savings_advice": ["save", "saving", "reduce", "cut"],
    "investment": ["invest", "stocks", "crypto", "mutual fund"],
}


def mock_keyword_intent(text: str):
    text_lower = text.lower()
    for intent, keywords in INTENTS.items():
        if any(k in text_lower for k in keywords):
            return {"intent": intent, "score": 0.9}
    return {"intent": "general", "score": 0.5}


def classify_intent(text: str):
    """Classify user text into intents using keyword or HuggingFace zero-shot."""
    # First, try keyword matching
    intent = mock_keyword_intent(text)
    if intent["intent"] != "general":
        return intent

    # Optional: HuggingFace zero-shot fallback
    if USE_HF and hf_classifier:
        labels = list(INTENTS.keys())
        result = hf_classifier(text, candidate_labels=labels)
        return {"intent": result["labels"][0], "score": result["scores"][0]}

    return {"intent": "general", "score": 0.5}
