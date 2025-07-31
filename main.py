# main.py
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "your-verify-token")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN", "your-page-access-token")

# --- Helper: Send a reply back ---
def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v19.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post(url, params=params, json=payload)

# --- Webhook Verification ---
@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        return challenge
    return "Unauthorized", 403

# --- Webhook Listener ---
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data["entry"]:
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]
                if "message" in messaging_event and "text" in messaging_event["message"]:
                    msg_text = messaging_event["message"]["text"].lower()
                    username = sender_id[-5:]  # default anonymized fallback

                    # Keyword logic
                    if "services" in msg_text:
                        reply = f"Hey {username}, here are some of our core services: Cybersecurity, Network Design, Backup & Disaster Recovery, and IT Consulting. More at https://www.primesecit.com/services"
                    elif "contact" in msg_text or "talk" in msg_text:
                        reply = f"Thank you for reaching out to PrimeSec IT {username}. Your request has been received and is currently under review. A member of our team will get back to you as soon as possible — typically within one business day. We appreciate your patience and the opportunity to support your IT needs."
                    else:
                        reply = f"Hey {username}, thanks for reaching out! You can learn more at https://www.primesecit.com. Let us know if you need help with services or support."

                    send_message(sender_id, reply)

    return "ok", 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
