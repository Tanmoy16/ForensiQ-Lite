# ai/llm_client.py

import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_report(findings_text):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a digital forensics report assistant."},
            {"role": "user", "content": findings_text}
        ],
        temperature=0.2,
        max_tokens=500
    )
    return response.choices[0].message["content"]
