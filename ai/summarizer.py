from ctransformers import AutoModelForCausalLM

MODEL_PATH = "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

# CRITICAL FIX: Set context_length to 4096 (Mistral supports up to 32k, but 4k is safe for CPU)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    model_type="mistral",
    gpu_layers=0,
    context_length=4096  # <--- THIS WAS MISSING
)

def generate_summary(timeline_text: str) -> str:
    prompt = f"""
You are a digital forensic analyst.

Based on the following forensic timeline, write a clear and concise
incident investigation summary. Identify suspicious behavior,
possible attack sequence, and attacker intent.

Timeline:
{timeline_text}

Investigation Summary:
"""
    # Calculate tokens safely (approximate)
    # If text is too long even for 4096, we truncate it here to prevent crash
    if len(prompt) > 12000: # ~3000 tokens
        prompt = prompt[:12000] + "\n...[Truncated]..."

    output = model(
        prompt,
        max_new_tokens=500, # Increased slightly for better reports
        temperature=0.2
    )
    return output.strip()