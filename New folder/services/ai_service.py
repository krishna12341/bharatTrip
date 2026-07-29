import os
import openai


class AIService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key

    def query(self, prompt: str):
        if not self.api_key:
            return {"error": "OpenAI API key is not configured."}
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an operations assistant for a refund management platform."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=600,
        )
        return {"answer": response.choices[0].message.content.strip()}
