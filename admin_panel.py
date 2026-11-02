import json, os
from flask import render_template_string, request, redirect
ADMIN_PASSWORD = "Nigro433" 
ADMIN_HTML = '''
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:Arial;background:#f0f2f5;margin:0;padding:10px}
.card{background:white;border-radius:10px;padding:15px;max-width:600px;margin:auto}
.item{display:block;text-decoration:none;color:black;border-bottom:1px solid #eee;padding:12px 5px}
.item:hover{background:#f5f5f5}
.badge{padding:2px 8px;border-radius:10px;font-size:11px;color:white}
.red{background:red} .green{background:green} .gray{background:gray}
</style>
</head>
<body>
<div class="card">
<h2>📨 Wateja Wote ({{ customers|length }})</h2>
<input type="text" id="search" placeholder="Tafuta namba..." onkeyup="filter()" style="width:100%;padding:10px;margin-bottom:10px">
{% for c in customers %}
<a class="item" href="/admin/chat/{{ c.uid }}?p={{ pwd }}">
  <b>{{ c.name }}</b> <span style="float:right">{{ c.count }} msg</span><br>
  <small>{{ c.last_text }}</small><br>
  {% if c.is_paused %}<span class="badge red">🔴 UMEZUIA BOT - Wewe unajibu</span>
  {% else %}<span class="badge green">🟢 BOT ANAFANYA KAZI</span>{% endif %}
</a>
{% endfor %}
{% if not customers %}<p>Hakuna mteja bado. Mteja akituma ujumbe WhatsApp ataonekana hapa.</p>{% endif %}
</div>
<script>
function filter(){
  let q=document.getElementById('search').value.toLowerCase();
  document.querySelectorAll('.item').forEach(el=>{
    el.style.display = el.innerText.toLowerCase().includes(q) ? 'block' : 'none';
  });
}
</script>
</body>
</html>
'''

# ===== HTML 2: CHAT YA MTEJA MMOJA - /admin/chat/<uid> =====
CHAT_HTML = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:Arial;background:#e5ddd5;margin:0}
.header{background:#075e54;color:white;padding:10px;position:sticky;top:0}
.chat{height:400px;overflow:auto;padding:15px;display:flex;flex-direction:column;gap:8px}
.msg{max-width:75%;padding:8px 12px;border-radius:8px;font-size:14px}
.user{background:white;align-self:flex-start}
.bot{background:#dcf8c6;align-self:flex-end}
.owner{background:#a0e7ff;align-self:flex-end;border:1px solid #0084ff}
.form{background:white;padding:10px;display:flex;gap:5px;position:sticky;bottom:0}
input[type=text]{flex:1;padding:12px;border-radius:20px;border:1px solid #ccc}
button{padding:10px 15px;border:none;border-radius:20px;cursor:pointer}
</style>
</head>
<body>
<div class="header">
  <a href="/admin?p={{ pwd }}" style="color:white;text-decoration:none">⬅ Rudi</a> 
  &nbsp;&nbsp; <b>Chat na {{ uid }}</b> {{ profile.get('name','') }}<br>
  {% if is_paused %}<small style="color:#ffbaba">🔴 BOT AMEZUIWA - Wewe ndio unajibu</small>
  {% else %}<small style="color:#b7ffbf">🟢 BOT ANAFANYA KAZI</small>{% endif %}
</div>

<div class="chat" id="chat">
{% for m in msgs %}
  <div class="msg {% if m.get('source')=='OWNER' %}owner{% elif m.get('role')=='user' %}user{% else %}bot{% endif %}">
    <b style="font-size:10px">{{ m.get('role','') }} {{ '(Wewe)' if m.get('source')=='OWNER' else '' }}</b><br>
    {{ m.get('text','') or m.get('parts',[''])[0] }}
  </div>
{% endfor %}
</div>

<form method="POST" class="form">
  <input type="text" name="text" placeholder="Jibu kama mmiliki..." required autocomplete="off">
  <button name="reply" value="reply" style="background:#075e54;color:white">Tuma</button>
</form>

<div style="background:white;padding:10px;display:flex;gap:10px;justify-content:center">
  <form method="POST"><button name="reply" value="pause" style="background:red;color:white">⏸️ ZUIA BOT - Mimi nashughulikia</button></form>
  <form method="POST"><button name="reply" value="resume" style="background:green;color:white">▶️ RUHUSU BOT - Arudi kazini</button></form>
</div>

<script>document.getElementById('chat').scrollTop = 999999;</script>
</body>
</html>
"""
def register_admin(app, memory, send_whatsapp_reply):
# ROUTE 1: ORODHA YA WATEJA WOTE - Hii ndio mfanyabiashara ataona kwanza
    @app.route("/admin", methods=["GET"])
    def admin():
        if request.args.get("p") != ADMIN_PASSWORD: 
            return "Password mbaya ?p=Nigro433"

        data = load_data()
        chats = data.get("chats", {})
        paused = data.get("paused_users", {})
        profiles = data.get("profiles", {})

    # Tengeneza list ya wateja na last message - ndio iwe general
        customers = []
        for uid, msgs in chats.items():
            if not msgs: continue
            last = msgs[-1]
            customers.append({
            "uid": uid,
                "name": profiles.get(uid, {}).get("name", uid),
                "last_text": last.get("text", "")[:35],
                "last_time": last.get("time", ""),
                "count": len(msgs),
                "is_paused": uid in paused,
                "needs_owner": last.get("source") != "OWNER" and "mmiliki" in last.get("text","").lower()
            })
    # Wapange - waliochat karibuni na walio-pause juu
        customers.sort(key=lambda x: (not x['is_paused'], -x['count']))

        return render_template_string(ADMIN_HTML, chats=chats, profiles=profiles, 
                                  customers=customers, pwd=ADMIN_PASSWORD)

# ROUTE 2: CHAT YA MTEJA MMOJA - "Chat na 255..."
        @app.route("/admin/chat/<uid>", methods=["GET", "POST"])
        def admin_chat(uid):
            if request.args.get("p") != ADMIN_PASSWORD: 
                return "Password mbaya"
 
            data = load_data()

            if request.method == "POST":
                action = request.form.get("reply") # hapa umetumia "reply" kwa action zote

                if action == "pause":
                    data.setdefault("paused_users", {})[uid] = {"paused_at": time.time(), "by": "admin"}
                    save_data(data)
                    return redirect(f"/admin/chat/{uid}?p={ADMIN_PASSWORD}")

                if action == "resume":
                    data.setdefault("paused_users", {}).pop(uid, None)
                    save_data(data)
                    return redirect(f"/admin/chat/{uid}?p={ADMIN_PASSWORD}")

                if action == "reply":
            # Mfanyabiashara ametuma ujumbe kama mmiliki
                    text = request.form.get("text") or request.form.get("message") or request.form.get("reply_text")
                    if text and text not in ["pause", "resume", "reply"]:
                # 1. Tuma WhatsApp kweli
                        send_whatsapp_reply(uid, text)
                # 2. Hifadhi kwenye chats ili ionekane kwenye admin
                        data.setdefault("chats", {}).setdefault(uid, []).append({
                        "role": "model", "text": text, "source": "OWNER", "time": time.time()
                        })
                # 3. Pause huyo mteja automaticaly ili bot asimjibu tena
                        data.setdefault("paused_users", {})[uid] = {"paused_at": time.time(), "by": "admin_reply"}
                        save_data(data)

                return redirect(f"/admin/chat/{uid}?p={ADMIN_PASSWORD}")

    # GET - Onyesha chat
            msgs = data.get("chats", {}).get(uid, [])
            profile = data.get("profiles", {}).get(uid, {})
            is_paused = uid in data.get("paused_users", {})

            return render_template_string(HTML_CHAT, uid=uid, msgs=msgs, 
                                  profile=profile, is_paused=is_paused, 
                                  pwd=ADMIN_PASSWORD, all_chats=data.get("chats",{}))
