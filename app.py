import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app, origins="*")

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "GiftIdeas AI backend is running!"})


@app.route("/get-gifts", methods=["POST"])
def get_gifts():
    try:
        body = request.get_json()

        relation  = body.get("relation", "Friend")
        age       = body.get("age", "25")
        gender    = body.get("gender", "not specified")
        occasion  = body.get("occasion", "Birthday")
        budget    = body.get("budget", "Rs.1500")
        interests = body.get("interests", "not specified")
        styles    = body.get("styles", "not specified")
        brands    = body.get("brands", "not specified")
        extra     = body.get("extra", "none")

        prompt = f"""You are an expert gift recommendation assistant for Indian users.
Generate 6 highly personalised gift suggestions based on these details:

- Recipient: {relation}, gender: {gender}, age: {age}
- Occasion: {occasion}
- Budget: {budget} (stay within this budget)
- Interests/hobbies: {interests}
- Style preferences: {styles}
- Favourite brands: {brands}
- Extra context: {extra}
- Country: India (suggest products available in India, all prices in INR)

Respond ONLY with valid JSON. No markdown, no extra text outside the JSON.
Format:
{{
  "title": "6 Gifts for Mom's Birthday",
  "subtitle": "one warm sentence describing the curation",
  "gifts": [
    {{
      "name": "Specific product name",
      "price": "Rs.XXX - Rs.XXX",
      "reason": "2 sentences why this is perfect for this person and occasion",
      "tags": ["tag1", "tag2", "tag3"],
      "where": "Amazon India / Flipkart / Local store"
    }}
  ]
}}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.7
        )

        raw = response.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        data = json.loads(raw)
        return jsonify(data)

    except json.JSONDecodeError:
        return jsonify({"error": "AI returned invalid response. Please try again."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
