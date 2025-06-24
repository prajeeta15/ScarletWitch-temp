# gpt_assist.py
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")


def gpt_refine_threat(text, original_score):
    prompt = f"""
You are a cybersecurity AI evaluating dark web content.

Text:
\"\"\"
{text}
\"\"\"

The current predicted threat score is {original_score} (range: 0–10).

Re-evaluate and return a new score (0–10) based on hidden threats, slang, context. 
Respond ONLY with the score. Example: 7.8
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a threat assessment assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.2
        )
        score = float(response.choices[0].message.content.strip())
        return round(min(max(score, 0), 10), 2)  # clamp to 0–10
    except Exception as e:
        print(f"GPT failed: {e}")
        return original_score  # fallback
