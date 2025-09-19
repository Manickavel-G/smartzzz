import os
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

def build_prompt(user_type, intent, summary, user_msg):
    """
    Build prompt for LLM response generation.
    """
    return f"""
You are a financial advisor for a {user_type}.
User intent: {intent}
Message: {user_msg}
Summary: {summary}
Generate a short, helpful answer with 2 bullet points + an action step.
"""

USE_GRANITE = os.getenv("USE_GRANITE", "false").lower() == "true"

# Load IBM Granite model and tokenizer if enabled
granite_tokenizer = None
granite_model = None
granite_pipeline = None
if USE_GRANITE:
    granite_model_name = "ibm/granite-7b"
    granite_tokenizer = AutoTokenizer.from_pretrained(granite_model_name)
    granite_model = AutoModelForCausalLM.from_pretrained(granite_model_name, torch_dtype=torch.float16, device_map="auto")
    granite_pipeline = pipeline("text-generation", model=granite_model, tokenizer=granite_tokenizer, device=0)

def generate_response_with_granite(prompt):
    """
    Generate response using IBM Granite model.
    """
    if not granite_pipeline:
        return "IBM Granite model is not enabled."
    outputs = granite_pipeline(prompt, max_length=200, do_sample=True, temperature=0.7)
    return outputs[0]['generated_text']

def generate_response(user_type, intent, summary, user_msg):
    """
    Generate response text (fallback template for hackathon demo).
    """
    prompt = build_prompt(user_type, intent, summary, user_msg)

    if USE_GRANITE:
        return generate_response_with_granite(prompt)

    # Fallback deterministic template
    if intent == "budget":
        return f"📊 Your monthly savings: {summary['savings']} ({summary['savings_rate']}%)."
    elif intent == "savings_advice":
        return "💡 Suggestion:\n- Automate savings transfer.\n- Track discretionary spend.\nAction: Set aside 5–10%."
    elif intent == "investment":
        return "📈 Consider SIPs, low-risk funds.\nAction: Start with small, regular investments."
    else:
        return "🤖 I'm here to help with budgeting, savings, or investments."
