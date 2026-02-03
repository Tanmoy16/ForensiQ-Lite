from ctransformers import AutoModelForCausalLM

MODEL_PATH = "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    model_type="mistral",
    gpu_layers=0  # keep 0 for CPU
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
    output = model(
        prompt,
        max_new_tokens=350,
        temperature=0.2
    )
    return output.strip()
