from groq import Groq
import os


client = Groq(
    api_key=os.getenv("groq_api")
)


def generate_answer(
    question: str,
    chunks
):
    # Convert retrieved chunks into context
    context = "\n\n".join(
        chunk.content
        for chunk in chunks
    )

    prompt = f"""
You are a university assistant.

Answer the user's question using only the provided context.

If the answer cannot be found in the context, say that you
do not have enough information.

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content