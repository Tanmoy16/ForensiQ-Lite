from ctransformers import AutoModelForCausalLM

MODEL_PATH = "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

# M1 OPTIMIZED CONFIGURATION
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    model_type="mistral",
    # Try 50 to offload to GPU. If it crashes, set back to 0.
    gpu_layers=50, 
    # M1 can easily handle 8k context (Mistral supports up to 32k)
    context_length=8192 
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
    # Safe truncation for 8k context (leaving ~2k for generation)
    if len(prompt) > 24000: 
        prompt = prompt[:24000] + "\n...[Truncated]..."

    output = model(
        prompt,
        max_new_tokens=1000, # Generate longer, more detailed reports
        temperature=0.2
    )
    return output.strip()