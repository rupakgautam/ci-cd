import json

import ollama


def load_prompt():
    """Load the prompt template."""
    prompt_path = "prompts/rag_prompt_v1.txt"

    with open(prompt_path) as f:
        return f.read()


def generate_answer(question, context):
    """Generate an answer using the LLM with the prompt and model."""
    system_prompt = load_prompt()

    prompt = f"""
{system_prompt}

Context:
{context}

Question:
{question}
"""

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response["message"]["content"]
    return parse_response(raw)


def parse_response(raw_text):
    """Parse the LLM response, extracting structured JSON if present.

    Returns a dict with 'answer' and 'citations' keys.
    Falls back to raw text if JSON parsing fails.
    """
    try:
        # Try to extract JSON from the response
        text = raw_text.strip()

        # Handle case where LLM wraps JSON in markdown code blocks
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first and last lines (```json and ```)
            text = "\n".join(lines[1:-1])

        data = json.loads(text)

        if "answer" in data:
            return {
                "answer": data["answer"],
                "citations": data.get("citations", []),
                "raw": raw_text
            }
    except (json.JSONDecodeError, KeyError):
        pass

    # Fallback: return raw text with no structured citations
    return {
        "answer": raw_text,
        "citations": [],
        "raw": raw_text
    }
