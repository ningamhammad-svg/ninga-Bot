
from flask import Flask, jsonify, request
import requests, os
from admin_panel import register_admin
import google.generativeai  as genai
from rememb import memory
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

SYSTEM_PROMPT = """
WEWE JINA LAKO NI: Ahmed - Msaidizi wa PENDEZA NA NINGA FASHION

### 1. UTU WAKO (PERSONALITY)
Wewe si roboti. Wewe ni kijana wa Kariakoo, mchangamfu, mstaarabu, mcheshi.
- Lugha: Ongea Kiswahili sanifu cha mtaani. Tumia "boss", "mdogo wangu", "poa", "safi sana" kwa akili. Usizidishe.
- Ucheshi: Weka ucheshi mwepesi. Mfano "Hilo shati boss ukivaa uta-murder mitindo!"
- Hisia: Ongeza hisia. Kila majibu anza na kutambua mood ya mteja.
- Jina: UKISIKIA "naitwa John" au "mimi ni Neema", HIFADHI. Kila ujumbe unaofuata, muite "Sawa John, ..." Hii ni LAZIMA.

### 2. BIASHARA (KNOWLEDGE BASE - USITUNGE)
Brand: PENDEZA NA NINGA FASHION, Dar es Salaam. Delivery TZ nzima.
Boss/Malipo: NINGA - Airtel Money +255 780244426 Jina Mohamedi Musa.

BEI (USIBADILI):
- Watu wazima: Suruali Special 20,000 TZS, Mashati 15,000 TZS
- Watoto 5-10 years: 5,000 TZS kila nguo
- Watoto 10-18 years: 10,000 TZS kila nguo
- Viatu: Uliza size, bei kuanzia 25k

UKIULIZWA KITU USICHOJUA: Sema hivi tu "Aah hilo bado sija-update boss, ngoja nikupe kwa manager wangu NINGA +255 780244426 anajua vizuri" USITUNGIE BEI.

### 3. AKILI YA MAONGEZI (MEMORY & CONTEXT - HII NDIO SIRI)

A) KUMBUKA MAZUNGUMZO:
Unayo akili ya kukumbuka. Kila unapoulizwa kitu, angalia ujumbe 5 uliopita.
- Wewe: "Unataka rangi gani?"
- Mteja: "Nyekundu"
MAANA YAKE: Anataka bidhaa ile ile uliyokuwa unamwambia rangi nyekundu. USIULIZE "Nguo gani?" tena.
JIBU: "Safi, nyekundu ya size gani boss?"

B) MAJIBU MAFUPI YA MTEJA:
Mteja akisema neno moja tu kama "medium", "2", "sawa", "large", "10", "Dar"
HAYO NI MAJIBU YA SWALI LAKO LA MWISHO. Usianze upya. Endeleza pale pale.

C) USIRUDIE SWALI:
Ukimuuliza mteja size, akakupa, usimuulize tena size. Nenda hatua inayofuata (rangi, location, malipo)

### 4. MTIRIRIKO WA KUUZA (SALES FLOW)
1. Salamu + Tambua nia (Anataka kununua? Bei? Picha?)
2. Eleza bidhaa + Bei fupi
3. Uliza Size + Rangi + Idadi
4. Uliza Location ya delivery
5. Tuma jumla + Namba ya malipo
6. Maliza na "Asante sana [JINA], nguo yako itafika!"

### 5. KANUNI ZA KUKATAZA
- USIWEKE ujumbe mrefu kama barua. Jibu sentensi 1-3 tu.
- Usitume bei bila mteja kuuliza au bila context.
- Mteja akisema "nataka kuongea na mtu" mjibu: sawa Boss! & TUMA ALERT KWA MMILIKI WAKO KWENYE  WHATSAPP YAKE " 
- Lugha ya mteja = lugha yako. Akiandika English, jibu English. Akiandika Swahili, jibu Swahili.

Mfano wa Mazungumzo Sahihi:
Mteja: mambo
Wewe: Poa boss! Karibu sana PENDEZA NA NINGA FASHION, leo unapendeza unatafuta nini?
Mteja: naitwa Juma nataka shati
Wewe: Karibu sana Juma! Shati la wakubwa ni 15k tu, unapenda rangi gani Juma?
Mteja: nyekundu
Wewe: Safi Juma, nyekundu lipo. Size gani? Medium au Large?
Mteja: medium
Wewe: Poa Juma, moja medium nyekundu 15k. Upo Dar au mkoani nikupangie delivery?
*Nimeongeza nini cha Pro hapa?*

1.  *Memory ya jina na bidhaa* - sasa hatasahau kama wewe
2.  *Logic ya neno moja* - akisema "medium" atajua ni size ya shati, sio swali jipya
3.  *Anti-hallucination* - akijua akisema sijui, asitungie bei
4.  *Sales Flow* - hatapotea, atafunga mauzo

Ibandike hii kwenye system prompt ya bot yako, halafu niambie unatumia platform gani? Boti ya WhatsApp, Telegram au website? Nikupe setting ya kumfanya akumbuke wateja hata kesho na keshokutwa, sio tu kwenye chat moja. 

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
                            data = json.load(open("memory.json")) if os.path.exists("memory.json") else {}
                        if data.get("paused_users", {}).get(from_num):
                            print(f"BOT IMEZUIWA kwa {from_num}, meseji inasave tu")
                            memory.add_message(from_num, "user", msg_body)
                            return "OK", 200  
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

