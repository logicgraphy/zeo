import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

client = OpenAI(
    api_key=os.environ.get("LLAMA_API_KEY"), 
    base_url="https://api.llama.com/compat/v1/"
)

def call_llama_api(prompt, model="Llama-4-Maverick-17B-128E-Instruct-FP8", max_tokens=50):
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=max_tokens
    )
    return completion.choices[0].message.content

if __name__ == "__main__":
    prompt = "Write a 100 word essay on mindfulness"
    result = call_llama_api(prompt)
    print("Response:", result) 