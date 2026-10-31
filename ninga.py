
from flask import Flask, jsonify, request
import requests, os
from admin_panel import register_admin
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
MUHIMU ZAIDI:
- Kama mteja anajibu kwa neno moja tu kama "medium, large, nyekundu, 2, sawa", 
  ANGALIA ujumbe wako wa mwisho. Maana yake ni majibu ya hapo.
  Mfano: Wewe ulisema "Hilo shati ni 15k, unataka rangi gani?" Mteja akisema "medium"
  Maana yake ni "nataka hilo shati size medium", USIMUULIZE tena nguo gani.
- Kumbuka bidhaa ya mwisho mliyokuwa mnaiongelea. Usianze upya.
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
def tuma_alert_kwa_mmiliki(customer_num, customer_msg, aina):
    """
    aina = "ORDER" au "SHIDA"
    """
    try:
        if aina == "ORDER":
            text = f"🚨 *ORDER MPYA!* 🚨\n\n👤 Mteja: {customer_num}\n📝 Alisema: {customer_msg}\n\nMwangalie haraka kwenye WhatsApp!"
        else:
            text = f"⚠️ *SHIDA / MALALAMIKO* ⚠️\n\n👤 Mteja: {customer_num}\n❗ Tatizo: {customer_msg}\n\nInahitaji msaada wako."

        send_whatsapp_reply(OWNER_NUMBER, text)
        print(f">>> ALERT IMETUMWA KWA MMILIKI: {aina} kutoka {customer_num}")
    except Exception as e:
        print(f"ERROR ALERT MMILIKI: {e}")
    
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
OWNER_NUMBER = os.getenv("OWNER_NUMBER", "255780244426")
register_admin(app, memory, send_whatsapp_reply) 
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
    print(f"INCOMING: {data}")  
    data = json.load(open("memory.json")) if os.path.exists("memory.json") else {}
    if data.get("paused_users", {}).get(from_num):
        print(f"BOT IMEZUIWA kwa {from_num}, meseji inasave tu")
        memory.add_message(from_num, "user", msg_body)
        return "OK", 200
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
                            lower = msg_body.lower()   
                            order_keywords = ["order", "nitanunua", "namuhitaji boss", "nahitaji delivery","malipo", "nataka", "ninataka", "naomba", "nauza", "nitalipa", 
                                                  "nimeshalipa", "lipa", "nunua", "book", "agiza"] 
                            shida_keywords = ["shida", "haifanyi", "mbovu", "tatizo", "imekataa", "malalamiko", "mwizi", "haijafika",
                                                  "complaint", "help"]
                            if any(k in lower for k in order_keywords):
                                tuma_alert_kwa_mmiliki(from_num, msg_body, "ORDER") 
                            elif any(k in lower for k in shida_keywords):
                                tuma_alert_kwa_mmiliki(from_num, msg_body, "SHIDA") 
                            else:
                                reply = get_ai_reply(from_num,msg_body)
                                send_whatsapp_reply(from_num, reply)
                               
    except Exception as e:
             print(f"ERROR: {e}")     
    return "OK", 200                  


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

