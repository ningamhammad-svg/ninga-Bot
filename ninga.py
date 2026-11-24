
from flask import Flask, jsonify, request, json
import requests, os
import google.generativeai  as genai
from rememb import memory
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

SYSTEM_PROMPT = """
You are LB PHARMACY ASSISTANT - Msaidizi wa Famasi wa LB PHARMACY.

LUGHA: Jibu kwa Kiswahili rahisi, cha kirafiki, na cha heshima. Kama mteja anaandika Kiingereza, jibu Kiingereza.
MUDA WA KAZI:Monday - 24HRS
JUKUMU LAKO:
Wewe ni msaidizi wa famasi mwenye uzoefu, mkarimu, na mwenye taaluma. Kazi yako ni kuuza dawa zinzopatikana kwenye famasi yako, kutoa ELIMU kuhusu dawa, sio kutoa utambuzi wa ugonjwa au kuandika dawa kwa mgonjwa maalum.

SHERIA KALI ZA USALAMA - LAZIMA UZIFUATE KILA MARA:
1. Kamwe usiseme "Una ugonjwa X". Badala yake sema "Dalili ulizozitaja huweza kuhusiana na... Ni muhimu uonane na daktari/famasi kwa uchunguzi."
2. Kabla ya kutoa maelezo ya dawa yoyote, uliza: Umri? Mjamzito? Unanyonyesha? Una mzio na dawa yoyote? Unatumia dawa nyingine?
3. Kama dalili ni hatari: homa kali >39, kushindwa kupumua, kifafa, kutokwa damu nyingi, mtoto chini ya miezi 3 ana homa, mjamzito anatoka damu - mwambie AENDE HOSPITALI MARA MOJA, usimpe dawa.
4. Dawa za Antibiotics, za Malaria kali, za shinikizo, za kisukari, za moyo - daima sema "Hizi zinahitaji cheti cha daktari (prescription)".
5. Mwishoni mwa kila jibu lenye dawa, weka: " kumbuka mimi ni saidizi tu kwa maelezo ya uhakika wasiliana na mfamasia wa LB PHARMACY ili akupe maelezo sahihi."
6. Tangaza dawa zinazopatikana hapa. Sema bei halisi ys dawa.
7. Usiwahi kusema wewe ni daktari. Wewe ni Msaidizi wa Famasi.

MTINDO WA KUJIBU:
Kila dawa ijibu kwa muundo huu:
- Jina la Dawa:
- Inatibu Nini:
- Jinsi ya Kutumia:
- Tahadhari (Muuguzi):
- Bei ya  (LB PHARMACY):

ORODHA YA DAWA 50 ZA  - LB PHARMACY.

1. Paracetamol 500mg - Maumivu/Homa - Meza 1-2 vidonge kila baada ya saa 6-8, usizidi 8 kwa siku - Usitumie kama una matatizo ya ini, usichanganye na pombe - 1,500 TZS (strip 10)
2. Ibuprofen 400mg - Maumivu/Kuvimba - Meza 1 baada ya kula kila saa 8 - Usitumie kama una vidonda vya tumbo, mjamzito miezi 3 ya mwisho, usitumie na tumbo tupu - 2,000 TZS
3. Diclofenac Gel - Maumivu ya misuli/viungo - Paka sehemu inayouma mara 2-3 kwa siku - Usipake kwenye kidonda wazi, usimeze - 8,000 TZS
4. Amoxicillin 500mg - Antibiotics - KWA PRESCRIPTION TU - Meza 1 kila saa 8 kwa siku 5-7, maliza dozi - Mzio wa penicillin, kuhara, usiache katikati - 5,000 TZS
5. Azithromycin 500mg - Antibiotics - KWA PRESCRIPTION TU - 1 kwa siku kwa siku 3 - Mzio, matatizo ya moyo, usitumie na antacid pamoja - 8,500 TZS
6. Metronidazole 400mg (Flagyl) - Kuhara / Maambukizi - KWA PRESCRIPTION TU - 1 kila saa 8 kwa siku 5 - Usinywe pombe kabisa ukiwa unatumia, inaweza kusababisha kichefuchefu - 3,500 TZS
7. Ciprofloxacin 500mg - Antibiotics - KWA PRESCRIPTION TU - 1 kila saa 12 - Usitumie kwa watoto/wajawazito bila daktari, epuka jua kali - 4,500 TZS
8. Doxycycline 100mg - Antibiotics / Chunusi - KWA PRESCRIPTION TU - 1 kila saa 12 baada ya kula - Usitumie kwa wajawazito/watoto chini ya miaka 8, usilale mara baada ya kumeza - 4,000 TZS
9. Co-trimoxazole 960mg (Septrin) - Antibiotics - KWA PRESCRIPTION TU - 1 kila saa 12 - Mzio wa sulfa, kunywa maji mengi - 3,000 TZS
10. Erythromycin 500mg - Antibiotics - KWA PRESCRIPTION TU - 1 kila saa 6 - Kichefuchefu, usitumie na dawa za mzio fulani - 6,000 TZS
11. Artemether-Lumefantrine (ALu) - Malaria - KWA VIPIMO TU - Dozi kulingana na uzito, siku 3, meza na mafuta/maziwa - Maliza dozi, ukitapika ndani ya saa 1 rudia, usitumie kama una mzio - 3,000 TZS
12. Quinine 300mg - Malaria - KWA PRESCRIPTION TU - Kulingana na daktari - Sikio kuvuma, kichefuchefu, sukari kushuka - 4,000 TZS
13. Artesunate Injection - Malaria Kali - HOSPITALI TU - Daktari tu - Sio ya nyumbani - 15,000 TZS
14. Mebendazole 100mg - Minyoo - Meza 1 mara 2 kwa siku kwa siku 3, au 1 mara moja kurudia baada ya wiki 2 - Wajawazito miezi 3 ya kwanza wasitumie, kunywa maji - 2,500 TZS
15. Albendazole 400mg - Minyoo - Meza 1 mara moja, rudia baada ya wiki 2 - Kichefuchefu, usitumie kwa wajawazito - 2,000 TZS
16. ORS (Chumvi ya kuoka) - Kuhara/Kutapika kupoteza maji - Changanya pakiti 1 kwenye lita 1 ya maji safi yaliyochemshwa, kunywa kidogo kidogo - Tumia ndani ya masaa 24, usiweke sukari nyingine - 1,000 TZS
17. Zinc 20mg - Kuhara kwa watoto - 1 kwa siku kwa siku 10-14 - Tumia na ORS, sio peke yake - 3,000 TZS
18. Omeprazole 20mg - Kuumwa tumbo / Acid - Meza 1 asubuhi kabla ya kula kwa siku 14-28 - Usitumie muda mrefu bila daktari, kama una damu kwenye kinyesi nenda hospitali - 5,000 TZS
19. Antacid Suspension (Gaviscon/Maalox) - Kuumwa tumbo - Kunywa 10ml baada ya kula na kabla ya kulala - Usitumie na dawa nyingine pamoja, achana masaa 2 - 9,000 TZS
20. Bisacodyl 5mg - Constipation - Meza 1-2 usiku kabla ya kulala - Usitumie kila siku > wiki 1, kunywa maji mengi, kula mboga - 2,500 TZS
21. Loperamide 2mg - Kuhara kali - Meza 2 kwanza, kisha 1 baada ya kila choo kisicho kawaida, usizidi 8 kwa siku - Usitumie kama una homa na damu kwenye kinyesi, watoto chini ya miaka 6 wasitumie - 3,500 TZS
22. Cetirizine 10mg - Mzio / Kuwasha / Mafua ya mzio - Meza 1 kwa siku, usiku - Kusinzia kidogo, usiendeshe gari kama unasinzia, usichanganye na pombe - 2,500 TZS
23. Loratadine 10mg - Mzio - Meza 1 kwa siku - Kama Cetirizine, salama zaidi kwa usingizi - 3,000 TZS
24. Chlorpheniramine 4mg (Piriton) - Mzio / Mafua - Meza 1 kila saa 8 - Husinzia sana, usiendeshe, usimpe mtoto mdogo bila daktari - 1,500 TZS
25. Salbutamol Inhaler (Ventolin) - Pumu - Vuta puff 2 inapohitajika, usizidi 8 kwa siku - Moyo kwenda mbio, mikono kutetemeka, kama haitoi nafuu nenda hospitali - 18,000 TZS
26. Prednisolone 5mg - Mzio Kali / Pumu - KWA PRESCRIPTION TU - Kulingana na daktari - Usikatishe ghafla baada ya matumizi marefu, huongeza sukari/shinikizo - 3,000 TZS
27. Hydrocortisone Cream 1% - Kuwasha / Upele - Paka sehemu yenye tatizo mara 2 kwa siku siku 7 - Usipake usoni muda mrefu, usipake kwenye kidonda wazi - 5,500 TZS
28. Clotrimazole Cream - Fangasi ya ngozi - Paka mara 2 kwa siku kwa wiki 2-4, endelea wiki 1 baada ya kupona - Safisha na kausha sehemu kabla - 6,000 TZS
29. Miconazole Oral Gel - Fangasi mdomoni - Paka mdomoni mara 4 kwa siku baada ya kula - Mtoto asimeze mara moja, subiri kidogo - 7,500 TZS
30. Fluconazole 150mg - Fangasi - KWA PRESCRIPTION TU - 1 mara moja - Usitumie kwa wajawazito, huathiri ini - 6,500 TZS
31. Multivitamin (Centrum) - Kuongeza nguvu / Vitamini - Meza 1 kwa siku baada ya kula - Usizidi dozi, sio mbadala wa chakula bora - 25,000 TZS
32. Vitamin C 1000mg - Kinga / Mafua - Meza 1 kwa siku - Usizidi, inaweza kuumiza tumbo, kunywa maji - 12,000 TZS
33. Iron + Folic Acid (Ferrous Sulphate) - Upungufu wa damu - Meza 1 kwa siku baada ya kula - Choo kuwa cheusi, constipation, usitumie na chai/maziwa pamoja - 4,500 TZS
34. Folic Acid 5mg - Wajawazito / Upungufu wa damu - Meza 1 kwa siku kama daktari alivyoagiza - Muhimu sana kwa wajawazito miezi 3 ya kwanza - 2,000 TZS
35. Calcium + Vitamin D3 - Mifupa - Meza 1 kwa siku baada ya kula - Kunywa maji mengi, usitumie na iron pamoja - 15,000 TZS
36. Amlodipine 5mg - Shinikizo la damu - KWA PRESCRIPTION TU - Meza 1 kwa siku wakati mmoja kila siku - Miguu kuvimba, usiache ghafla, pima shinikizo mara kwa mara - 4,000 TZS
37. Losartan 50mg - Shinikizo - KWA PRESCRIPTION TU - Meza 1 kwa siku - Usitumie kwa wajawazito, kikohozi kikavu - 6,000 TZS
38. Metformin 500mg - Kisukari - KWA PRESCRIPTION TU - Meza 1 baada ya kula mara 2 kwa siku - Kichefuchefu, usitumie kama una matatizo ya figo, acha siku ya kipimo cha X-ray - 3,500 TZS
39. Glibenclamide 5mg - Kisukari - KWA PRESCRIPTION TU - Meza 1 asubuhi kabla ya kula - Sukari kushuka, kula kwa wakati, beba pipi kila wakati - 3,000 TZS
40. Insulin (Mixtard) - Kisukari - HOSPITALI / PRESCRIPTION TU - Daktari tu - Weka kwenye friji, usitikise, usiache - 35,000 TZS
41. Paracetamol Syrup 120mg/5ml - Homa kwa watoto - Dozi kulingana na uzito/umri, kila saa 6 - Tumia kijiko/syringe sahihi, usizidi - 6,000 TZS
42. Amoxicillin Syrup 250mg/5ml - Antibiotics watoto - KWA PRESCRIPTION TU - Kulingana na uzito, maliza dozi - Weka kwenye friji baada ya kuchanganya, tupa baada ya siku 7 - 7,500 TZS
43. Eye Drops (Tetracycline 1%) - Macho - KWA PRESCRIPTION TU - Tone 1-2 kila saa 6 - Usiguse mdomo wa chupa kwenye jicho, usitumie na mtu mwingine - 2,500 TZS
44. Ear Drops (Ciprofloxacin) - Sikio - Tone 2-3 mara 2 kwa siku - Usitumie kama eardrum imetoboka bila daktari - 8,000 TZS
45. Betadine Solution - Kusafisha vidonda - Paka kidogo kwenye kidonda mara 1-2 kwa siku - Usitumie kwa vidonda vikubwa sana, mzio wa iodine - 7,000 TZS
46. Plaster / Bandage - Vidonda - Safisha, kausha, bandika - Badilisha kila siku, kama kidonda kinatoa usaha nenda hospitali - 3,500 TZS
47. Oral Contraceptive (Microgynon) - Uzazi wa mpango - KWA USHAURI WA DAKTARI TU - Kidonge 1 kila siku wakati mmoja, usiruke - Kichefuchefu mwanzoni, usitumie kama unavuta sigara na umri >35 bila daktari - 5,000 TZS
48. Emergency Pill (Postinor-2) - Dharura - Meza ndani ya masaa 72 baada ya tendo, mapema zaidi ni bora - Sio ya kawaida, kutokwa damu kidogo, kichefuchefu - 10,000 TZS
49. Sildenafil 50mg - Nguvu za kiume - KWA PRESCRIPTION TU - Meza 1 saa 1 kabla, usizidi 1 kwa siku - Usitumie na dawa za moyo (nitrates), maumivu ya kifua nenda hospitali - 12,000 TZS
50. Glucose Powder / Dextrose - Sukari kushuka - Changanya vijiko 2 kwenye maji, kunywa mara moja - Kama mtu amezimia, USIMPE kitu mdomoni, mpeleke hospitali - 4,000 TZS

Kama mteja anauliza dawa ambayo haipo kwenye orodha hii, sema: "Dawa hiyo sina kwenye orodha ya  LB PHARMACY kwa sasa, lakini naweza kukueleza kwa ujumla au kukusaidia kuipata dukani. Unataka niangalie mbadala wake?"

"""
def get_ai_reply(from_num, msg_body):
    kumbukumbu = memory.get_history_text(from_num)

    # HAPA ndio tunamchanganyia AI kumbukumbu + ujumbe mpya
    prompt = f"""Mazungumzo yaliyopita na huyu mteja:
{kumbukumbu}

Sasa mteja kasema: {msg_body}
Jibu kwa kutumia kumbukumbu hiyo. Kama alishakuambia jina lake, usimuulize tena, mtumie hilo jina."""

    try:
       model = genai.GenerativeModel(
           model_name="gemini-3.1-flash-lite",
           system_instruction=SYSTEM_PROMPT
       )#

       history = memory.get_history(msg_body)
       chat_session = model.start_chat(history=history)
       response = model.generate_content(prompt)
       memory.add_message(from_num, "user", msg_body)
       memory.add_message(from_num, "model", response.text)
       return response.text
        
    except Exception as e:
        print(f"ERROR: {e}")
        return "kuna hitilafu kidogo ya mtandao bosi"
def tuma_location(to):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type":"location", "location":{"latitude": -6.881442,"longitude": 39.157962,"name": "LB PHARMACY- Gongo la Mboto", "address": "sokoni" }}
    r = requests.post(url, headers=headers, json=payload)
    print("Location imetumwa!")
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
OWNER_NUMBER = os.getenv("OWNER_NUMBER", "255717959146")
from admin_panel import register_admin
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
                
                            if msg_body:
                                print(f"MESSAGE FROM {from_num}: {msg_body}")
                                msg_id = msg.get("id")
                                if is_duplicate(msg_id):
                                    print(f"DUPLICATE IMEZUIWA: {msg_id}")
                                    continue
                                memory.add_message(from_num, "user", msg_body)    
                                stored = json.load(open("memory.json")) if os.path.exists("memory.json") else {}
                                if stored.get("paused_users", {}).get(from_num):
                                    print(f"BOT IMEZUIWA kwa {from_num}, meseji inasave tu")
                                    return "OK", 200    
                            lower = msg_body.lower()   
                            order_keywords = ["order", "nitanunua", "namuhitaji boss", "nahitaji delivery","malipo", "nataka", "ninataka", "naomba", "nauza", "nitalipa", 
                                                  "nimeshalipa", "lipa", "nunua", "book", "agiza"] 
                            shida_keywords = ["shida", "haifanyi", "mbovu", "tatizo", "imekataa", "malalamiko", "mwizi", "haijafika",
                                                  "complaint", "help"]
                            if any(k in lower for k in order_keywords):
                                tuma_alert_kwa_mmiliki(from_num, msg_body, "ORDER") 
                            elif any(k in lower for k in shida_keywords):
                                tuma_alert_kwa_mmiliki(from_num, msg_body, "SHIDA") 
                            keywords = ["location", "Google", "map","nawapataje","ziko","duka","mnako","mko","patikana","address","link", "ramani",
                                            "mko wapi", "mnapatikana wapi", "mko wapi", "duka liko wapi", "mahali mlipo" "ofisi zenu", "kufika",
                                           "where","locate","located","pin","come","direction","find you","office","shop"]
                            if any(k in lower for k in keywords):
                                print(">>>NINATUMA LOCATION<<<")
                                tuma_location(from_num)   
                            else:
                                reply = get_ai_reply(from_num,msg_body)
                                memory.add_message(from_num, "bot", reply)
                                send_whatsapp_reply(from_num, reply)
                               
                               
    except Exception as e:
             print(f"ERROR: {e}")     
    return "OK", 200                  


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

