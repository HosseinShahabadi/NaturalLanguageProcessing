import requests
import os
from openai import OpenAI

# --- Configuration ---

MODEL_NAME = "gpt-4.1-mini"  # The model you requested
MAX_TOKENS_FOR_SUMMARY = 500 # A bit of buffer over 450

class ApiClient:
    def __init__(self):
        self.model = MODEL_NAME
        self.client = OpenAI(
            base_url="https://api.metisai.ir/openai/v1",
            api_key=os.getenv("OPENAI_API_KEY") 
        )

    def _request(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": f"{prompt}. just print answer"}],
            max_tokens=MAX_TOKENS_FOR_SUMMARY,
            temperature=0.2
        )
        return response.choices[0].message.content.strip()


if __name__ == '__main__':
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✅ API Key found successfully.")
    else:
        print("❌ ERROR: The 'OPENAI_API_KEY' environment variable was not found.")
        print("Please make sure it is set correctly before running the script.")

    if api_key:
        Client = ApiClient()

        prompt = "Where is the capital of Iran and USA?"
        result = Client._request(prompt)

        print("\n--- API Response ---")
        print(result)
    else:
        print("\nScript halted because API key is missing.")

