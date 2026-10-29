import json, os
from flask import render_template_string, request, redirect
def register_admin(app, memory, send_whatsapp_reply):
    ADMIN_PASSWORD = "Nigro433" 
ADMIN_HTML = 
<h2>PENDEZA Admin - Chats</h2>
{% for uid, msgs in chats.items() %}
  <div style="border:1px solid #ccc;padding:10px;margin:10px">
    <b>Mteja: {{uid}}</b> - {{profiles.get(uid, {}).get('name','Hajajulikana')}}
    <br><a href="/admin/chat/{{uid}}?p={{pwd}}">Fungua Chat</a>
  </div>
{% endfor %}


CHAT_HTML = '''
<h2>Chat na {{uid}} - {{profiles.get(uid, {}).get('name','')}}</h2>
<div style="height:400px;overflow:auto;border:1px solid #000;padding:10px">
{% for m in msgs %}
  <p><b>{{m['role']}}:</b> {{m['parts'][0]}}</p>
{% endfor %}
</div>
<form method="POST">
  <input name="reply" style="width:80%" placeholder="Jibu kama mmiliki...">
  <button>Tuma</button>
</form>
<br><a href="/admin?p={{pwd}}">Rudi</a>
'''

@app.route("/admin")
def admin():
    if request.args.get("p") != ADMIN_PASSWORD: return "Password mbaya ?p=ninga123"
    data = json.load(open("memory.json")) if os.path.exists("memory.json") else {"chats":{}, "profiles":{}}
    return render_template_string(ADMIN_HTML, chats=data.get("chats",{}), profiles=data.get("profiles",{}), pwd=ADMIN_PASSWORD)

@app.route("/admin/chat/<uid>", methods=["GET","POST"])
def admin_chat(uid):
    if request.args.get("p") != ADMIN_PASSWORD: return "Password mbaya"
    if request.method == "POST":
        reply = request.form.get("reply")
        if reply:
            send_whatsapp_reply(uid, reply)
            memory.add_message(uid, "model", reply)
        return redirect(f"/admin/chat/{uid}?p={ADMIN_PASSWORD}")
    
    data = json.load(open("memory.json")) if os.path.exists("memory.json") else {"chats":{}}
    msgs = data.get("chats",{}).get(uid, [])
    profiles = data.get("profiles",{})
    return render_template_string(CHAT_HTML, uid=uid, msgs=msgs, profiles=profiles, pwd=ADMIN_PASSWORD)
