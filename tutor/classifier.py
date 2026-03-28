import json


def classify_message(client, message_text, grade_level):
    prompt = f"""Classify this student message. The student is in grade {grade_level}.

Return ONLY valid JSON with these fields:
- "subject": one of "math", "english", or "general"
- "topic": specific topic (e.g. "multiplication", "fractions", "essay_writing", "reading_comprehension", "grammar", "algebra", "geometry", etc.)
- "intent": one of "question", "homework_help", "chat", or "unclear"

Student message: {message_text}"""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20241022",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        # Extract JSON from response (handle markdown code blocks)
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        return json.loads(text)
    except (json.JSONDecodeError, IndexError, KeyError):
        return {"subject": "general", "topic": "general", "intent": "unclear"}


def classify_image(client, image_data, media_type):
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20241022",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": 'This is a homework photo from a student. Classify it. Return ONLY valid JSON with: "subject" (math/english/general), "topic" (specific topic), "intent" ("homework_help").',
                        },
                    ],
                }
            ],
        )
        text = response.content[0].text.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        return json.loads(text)
    except (json.JSONDecodeError, IndexError, KeyError):
        return {"subject": "general", "topic": "general", "intent": "homework_help"}
