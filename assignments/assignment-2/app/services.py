from openai import OpenAI

from app.settings import settings


def generate_response(prompt: str) -> str:
    client = OpenAI(
        base_url=settings.openai_base_url, api_key=settings.openai_api_key
    )

    completion = client.chat.completions.create(
        model="qwen3.6-flash",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    response = completion.choices[0].message.content
    return response or "No response from LLM"