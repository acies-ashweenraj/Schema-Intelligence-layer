from groq import Groq


class GroqClient:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def chat(self, prompt: str, model="llama-3.3-70b-versatile", temperature=0):
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content
