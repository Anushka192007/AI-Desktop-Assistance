from flask import Flask, request
import requests
import openai
import os
import json
from collections import defaultdict
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util
import pikepdf  # For PDF merging
import ngrok

# Initialize Flask app
app = Flask(__name__)



# Set your OpenAI API Key and Twilio WhatsApp sandbox number
oai_api_key = os.environ.get("OPENAI_API_KEY")
twilio_auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
twilio_whatsapp_number = 'whatsapp:+14155238886'  # Twilio Sandbox number
openai.api_key = oai_api_key

# In-memory conversation store (can be replaced with Redis/DB for persistence)
conversation_memory = defaultdict(list)

# Initialize the Sentence-BERT model for embeddings
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

# System prompt for GPT-3.5
gpt_prompt = (
    "You are a Class 10 CBSE Science teacher helping students prepare for their board exam. "
    "Follow the NCERT book. Keep explanations simple, include relevant keywords and diagrams where needed. "
    "Answer only if you’re sure. Give bullet points for long answers."
)

# Function to merge PDFs using pikepdf
def merge_pdfs(pdf_list, output_pdf_path):
    with pikepdf.Pdf.new() as merged_pdf:
        for pdf in pdf_list:
            with pikepdf.open(pdf) as pdf_file:
                merged_pdf.pages.extend(pdf_file.pages)
        merged_pdf.save(output_pdf_path)

# Webhook route for incoming WhatsApp messages
@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    incoming_data = request.form
    user_query = incoming_data.get('Body')  # Extract the user query
    from_number = incoming_data.get('From')  # Extract the sender's number

    # If no query found, return a response
    if not user_query:
        return "No query found"

    # Ask GPT to respond to the query
    gpt_response = ask_gpt(from_number, user_query)
    
    # Send the response back to the user via WhatsApp
    send_whatsapp_message(from_number, gpt_response)

    return "OK", 200

def ask_gpt(user_id, user_input):
    try:
        # Retrieve relevant context from NCERT PDF based on the user query
        relevant_context = retrieve_context_from_ncert(user_input)

        # Append the new user input to the conversation memory
        conversation = conversation_memory[user_id]
        conversation.append({"role": "user", "content": user_input})

        # Prepend the system prompt and relevant context to ensure the assistant stays on track
        messages = [{"role": "system", "content": gpt_prompt + " " + relevant_context}] + conversation


        # Request GPT-3.5 model to generate a response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        # Extract and clean the response from GPT
        reply = response.choices[0].message['content'].strip()

        # Save assistant's response to memory for future context
        conversation.append({"role": "assistant", "content": reply})

        return reply
    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, there was an error processing your query. Please try again later."

def send_whatsapp_message(to, message):
    # Twilio API endpoint for sending messages
    url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_account_sid}/Messages.json"
    
    # Data for the WhatsApp message
    data = {
        'From': twilio_whatsapp_number,
        'To': to,
        'Body': message
    }
    
    # Twilio authentication
    auth = (twilio_account_sid, twilio_auth_token)

    try:
        # Send the POST request to Twilio API
        requests.post(url, data=data, auth=auth)
    except Exception as e:
        print(f"Failed to send message via Twilio: {e}")

# Function to extract text from NCERT PDF using PyMuPDF
def extract_text_from_ncert(pdf_path):
    document = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text("text")
    return text

# Function to retrieve context based on the query (using embeddings)
def retrieve_context_from_ncert(query):
    # Extract text from the NCERT PDF (can be optimized to load once and cache)
    ncert_text = extract_text_from_ncert("C:\\Users\\hp\\Downloads\\10th maths.zip\\f.pdf")
   
    # Split the text into sentences or paragraphs (here we use paragraphs)
    paragraphs = ncert_text.split("\n\n")
    
    # Encode the query and paragraphs into embeddings
    query_embedding = sentence_model.encode(query, convert_to_tensor=True)
    paragraph_embeddings = sentence_model.encode(paragraphs, convert_to_tensor=True)
    
    # Calculate cosine similarities between the query and the paragraphs
    similarities = util.pytorch_cos_sim(query_embedding, paragraph_embeddings)[0]
    
    # Get the paragraph with the highest similarity
    most_similar_idx = similarities.argmax()
    relevant_context = paragraphs[most_similar_idx]
    
    return relevant_context

# Main entry point to run the Flask app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    #app.run(host='0.0.0.0', port=port, debug=True)


