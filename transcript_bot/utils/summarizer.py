"""Summarization module using OpenAI API."""

import os
import openai
from typing import Optional

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def summarize_text(text: str, language: str = "es") -> Optional[str]:
    """
    Summarize text using OpenAI GPT.

    Args:
        text: Text to summarize
        language: Language code for summary

    Returns:
        Summary text or None if error
    """
    try:
        # Determine language for prompt
        if language == "es":
            system_prompt = "Resume el siguiente texto en puntos clave concisos:"
        else:
            system_prompt = "Summarize the following text in concise bullet points:"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            max_tokens=300,
            temperature=0.3
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Summarization error: {e}")
        return None
