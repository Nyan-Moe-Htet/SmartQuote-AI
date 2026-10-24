
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.runpod.ai/v2/b1dd8hy2hqo1nb/openai/v1",
    api_key=os.environ["RUNPOD_API_KEY"],
)

response = client.chat.completions.create(
    model="glm-5.3",
    messages=[
        {
            "role": "user",
            "content": "Reply with: SmartQuote AI RunPod integration works."
        }
    ],
    max_tokens=100,
    reasoning_effort="low",
)

print(response.choices[0].message.content)
