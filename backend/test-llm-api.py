import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url="https://api.openai.com/v1"
)

try:
    print("Loaded API Key:", os.environ.get("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[{"role": "user", "content": "Say hello!"}]        
    )
    print("Success:", response.choices[0].message.content)
except Exception as e:
    print("Error:", e)