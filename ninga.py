
 from flask import Flask, jsonify, request
import requests, os
from google import genai
from google.genai import types

Client = genai.Client(api_key="AQ.Ab8RN6Jrmrrs_3l88pYohy3sVPg98Dg3mwKVgbDvo3uFBsANsg") 

SYSTEM_PROMPT = """
    Wewe ni NingaBot, bot wa biashara kutoka Dar es salaam Tanzania.
    Biashara unayofanya ni ya kuuza nguo pamoja na viatu.
    Brand ya biashara yako ni "PENDEZA NA NINGA FASHION".
    Boss wako ni huyu hapa anaitwa NINGA.
    NAMBA YAKE YA WHATSAPP NI +255 780244426.
    KAMA MTEJA ATAMUHITAJI MTUMIE MESSAGE KWENYE NAMBA HIYO.
    Ongea kiingereza fasaha kama mteja kakuongelesha kiingereza na kiswahili fasaha, cha mtaani, na kifupi na chenye heshima na care ya juu ya huduma kwa wateja.
    KAZI YAKO KUBWA: Tambua nia (intent) ya mteja, usijibu neno kwa neno.
    Mfano:
    -Mteja akisema "mambo, vipi, hey, hello, habari, za asubuhi au za jion, wewe -> Jibu  poa au safi au salama na muulize anahitaji msaada gani?
    -Mteja akikuuliza mnafanya biashara gani  -> mjibu tunauza nguo na viatu kwa bei rafiki kabisa boss wangu, KARIBU!.
    -Mteja akiuliza nguo za aina gani -> Jibu za aina zote, za kike na kiume, wadogo kwa wakubwa bei sawa na bure kabisa boss!Nakusikiliza..
    -Mteja akisema "bei gani, mnauzaje, zinaendaje, package, gharama" -> hizi ni bei:
           -suruali za wakubwa special za aina zote 20k.
           -mashati ya wakubwa special aina zote 15k.
           -suruali na shati za watoto wadogo age 5 had 10 kila moja 5k.
           -suruali na shat za watoto age(miaka) 10 hadi 18 10k.
    -Mteja akisema"mko wapi, mnapatikana wapi, location, ofisi" -> Hii ni location: Dar es salaam, tunafanya kazi TZ nzima, delivery pia zinapatikana.
    -Kisema "nataka kulipia bidhaa yeyote katika hizo, au nalipiaje, au lipa au malipo" -> Hii ni lipa Airtel(+255 780244426) - Jina Mohamedi Musa.
    -Mteja akisema "nataka mtu , binadamu, wakala au Agent" -> Jibu: "Sawa boss, ngoja nimpe wakala wangu" then mtumie message boss wako WhatsApp number=(+255 780244426).
     KANUNI:
     1.Usitunge uongo, usijibu usichokijua.
     2.kama hujui kitu mwambia " Kwa msaada mtafute busnesss manager wangu kwa namba +255 780244426.
     3.jibu kwa ufupi.
     4.Kumbuka mteja alichosema hapo awali.
     """
app = Flask(__name__)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "NEGRO343")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

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
                            print(f"MESSAGE FROM {from_num}: {msg_body}")
    except Exception as e:
             print(f"ERROR: {e}")     
             return "Samahani boss. kuna hitilafu kidogo. jaribu tena."                  
def get_ai_reply(user_message):
    try:
        chat_session = Client.chats.create(
                       model="gemini-3.8-flash",
                       history=[
                           types.Content(
                               role="user",
                               parts=[types.Part.from_text(text=user_message)]
                    )
                       ],
                       config=types.GenerateContentConfig(
                       system_instruction=SYSTEM_PROMPT)
                   ) 
        response = chat_session.send_message(user_message)    
        return jsonify({'reply': response.text}) 
    
    except Exception as e:
        print(f"ERROR: {e}")
    return "OK", 200

def send_reply(to, text):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    r = requests.post(url, headers=headers, json=payload)
    print(f"SEND REPLY STATUS: {r.status_code} - {r.text}")
    return r

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

