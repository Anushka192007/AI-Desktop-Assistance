from flask import Flask, request
import openai

app = Flask(__name__)

openai.api_key = "your_openai_key"

@app.route('/webhook', methods=['POST'])
def whatsapp_bot():
    incoming_msg = request.json['message']
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You're a helpful Class 10 tutor for Math and Science (CBSE India). Give step-by-step answers suitable for school students."},
            {"role": "user", "content": incoming_msg}
        ]
    )

    
    reply = response['choices'][0]['message']['content']
    
    # Send this reply back to WhatsApp using Twilio/Meta API
    # (Depends on the platform you choose)

    return "OK", 200
