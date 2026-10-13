from flask import Flask, request
import requests, os

app = Flask(__name__)

TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "NEGRO343")

@app.route("/", methods=["GET"])
def home():
    return "Bot iko hai!"

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Token si sahihi", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]
        from_num = msg['from']
        text = msg['text']['body']
        text_low = text.lower()

        if "habari" in text_low or "mambo" in text_low:
            reply = "Poa! Karibu Ninga Bot. Andika: bidhaa, bei, au msaada"
        elif "bidhaa" in text_low:
            reply = "Tuna: 1. Simu 2. Laptops 3. Vifaa vya umeme"
        else:
            reply = f"Umesema: {text}. Andika 'msaada' kwa maelekezo."

        url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
        headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
        payload = {"messaging_product": "whatsapp", "to": from_num, "text": {"body": reply}}
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(e)
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
