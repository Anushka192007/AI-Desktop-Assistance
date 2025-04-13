from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Securely get API key from environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY")  # Remove hardcoded key!

@app.route('/webhook', methods=['POST'])
def whatsapp_bot():
    try:
        # Get incoming message (structure depends on your messaging platform)
        data = request.json
        incoming_msg = data.get('message', '')
        
        if not incoming_msg:
            return jsonify({"error": "No message provided"}), 400

        # Generate AI response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You're a helpful Class 10 tutor for Math and Science (CBSE India). Give step-by-step answers suitable for school students."},
                {"role": "user", "content": incoming_msg}
            ]
        )

        # Extract response text
        reply = response.choices[0].message.content

        # Here you would add code to send reply via Twilio/Meta API
        # Example: twilio_client.messages.create(body=reply, ...)
        
        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
