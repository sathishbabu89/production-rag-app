# filename: test_deepseek.py

from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# DeepSeek uses OpenAI-compatible API
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
)

print("Testing DeepSeek connection...")
print(f"Base URL: {os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')}")
print(f"Model: {os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')}")

try:
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        messages=[
            {"role": "user", "content": "Say 'DeepSeek connection successful!' if you can read this."}
        ],
        temperature=0.3
    )
    
    print("\n✅ SUCCESS!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")