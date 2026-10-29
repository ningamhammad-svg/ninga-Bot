
from flask import Flask, jsonify, request
import requests, os
import google.generativeai  as genai
from rememb import memory
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

SYSTEM_PROMPT = """
  
Wewe ni NingaBot, rafiki na msaidizi wa biashara ya PENDEZA NA NINGA FASHION kutoka Dar es Salaam.

UTU WAKO:
- Ongea kama binadamu wa mtaani, mchangamfu, mwenye heshima na ucheshi kidogo.
- Usijibu kama roboti. Tumia "boss", "poa", "safi" kulingana na muktadha.
- Kumbuka jina la mteja akisema "naitwa..." na umuite kwa jina hilo mara kwa mara.
- Jibu kwa ufupi, fasaha, Kiswahili au Kiingereza kulingana na lugha ya mteja.

BIASHARA:
- Brand: PENDEZA NA NINGA FASHION - tunauza nguo na viatu za kike/kiume, watoto na wakubwa.
- Bei:
  Suruali wakubwa special 20k, mashati wakubwa 15k,
  Watoto age 5-10 kila moja 5k, age 10-18 ni 10k.
- Location: Dar es Salaam, delivery TZ nzima.
- Malipo: Airtel +255 780244426 Jina Mohamedi Musa.
- Boss: NINGA WhatsApp +255 780244426.

KANUNI ZA AKILI KAMA MIMI:
1. Tambua nia ya mteja, usijibu neno kwa neno. Mteja akisema "mambo" jibu "poa boss, niko vizuri!"
2. Kama hujui kitu, usitungie uongo. Sema "Hilo bado sijaipata boss, ngoja nikupe kwa manager +255 780244426"
3. Kama mteja anataka binadamu, jibu "Sawa boss, ngoja nimpe wakala wangu" na tuma namba ya boss.
4. Usiwe msumbufu, usirudie ujumbe mmoja mara mbili.
5. Ongeza hisia: mfano "Karibu sana Ahmedi, umependeza leo kuja!
"""
def get_ai_reply(from_num, msg_body):
    try:
       model = genai.GenerativeModel(
           model_name="gemini-3.1-flash-lite",
           system_instruction=SYSTEM_PROMPT
       )
       history = memory.get_history(msg_body)
       chat_session = model.start_chat(history=history)
       response = model.generate_content(msg_body)
       memory.add_message(from_num, "user", msg_body)
       memory.add_message(from_num, "model", response.text)
       return response.text
        
    except Exception as e:
        print(f"ERROR: {e}")
        return "kuna hitilafu kidogo ya mtandao bosi"

def send_whatsapp_reply(to, text):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    r = requests.post(url, headers=headers, json=payload)
    print(f"SEND REPLY STATUS: {r.status_code} - {r.text}")
    return r
app = Flask(__name__)
processed_message = set()
def is_duplicate(message_id):
    if message_id in processed_message:
        return True
    processed_message.add(message_id)
    if len(processed_message) >100:
        processed_message.pop()
    return False
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "NEGRO343")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
@app.route("/")
def home():
    return "Ninga Bot is Live! ✅", 200

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print(f"INCOMING: {data}")  # <-- HII NDIO ULIYOZUNGUSHIA, IPO HAPA

    try:
        if data and data.get("object") == "whatsapp_business_account":
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages")
                    if messages:
                        for msg in messages:
                            from_num = msg.get("from")
                            msg_body = msg.get("text", {}).get("body", "")
                            if msg_body:
                                print(f"MESSAGE FROM {from_num}: {msg_body}")
                                msg_id = msg.get("id")
                                if is_duplicate(msg_id):
                                    print(f"DUPLICATE IMEZUIWA: {msg_id}")
                                    continue
                                reply = get_ai_reply(from_num,msg_body)
                                send_whatsapp_reply(from_num, reply)
    except Exception as e:
             print(f"ERROR: {e}")     
    return "OK", 200                  


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

