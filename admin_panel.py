import json, os
from flask import render_template_string, request, redirect
def register_admin(app, memory, send_whatsapp_reply):
    ADMIN_PASSWORD = "Nigro433" 
    ADMIN_HTML = '''
 <h2>Chat na {{uid}}</h2>
    {% if paused %} <h3 style="color:red">⛔ BOT AMEZUIWA kwa mteja huyu</h3> {% else %} <h3 style="color:green">✅ BOT ANAFANYA KAZI</h3> {% endif %}
    <div style="height:400px;overflow:auto;border:1px solid #000;padding:10px">
    {% for m in msgs %}
      <p><b>{{m['role']}} ({{m.get('source','bot')}}):</b> {{m['parts'][0]}}</p>
    {% endfor %}
    </div>
    <form method="POST">
      <input name="reply" style="width:70%" placeholder="Jibu kama mmiliki...">
      <button name="action" value="reply">Tuma kama Mmiliki</button>
    </form>
    <br>
    <form method="POST">
      <button name="action" value="pause" style="background:red;color:white;padding:10px">⛔ ZUIA BOT - Mimi nashughulikia</button>
      <button name="action" value="resume" style="background:green;color:white;padding:10px">✅ RUHUSU BOT - Arudi kazini</button>
    </form>
    <br><a href="/admin?p={{pwd}}">Rudi</a>
    '''

    LIST_HTML = """
    <h2>PENDEZA Admin</h2>
    {% for uid, msgs in chats.items() %}
      <div style="border:1px solid #ccc;padding:10px;margin:10px">
        <b>{{uid}}</b> - {{profiles.get(uid, {}).get('name','')}} - Msgs: {{msgs|length}}
        {% if paused_users.get(uid) %} <span style="color:red"> [BOT IMEZUIWA] </span> {% endif %}
        <br><a href="/admin/chat/{{uid}}?p={{pwd}}">Fungua Chat</a>
      </div>
    {% endfor %}
    """
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
            if action == "pause":
                data.setdefault("paused_users", {})[uid] = True
                json.dump(data, open("memory.json","w"))
            elif action== "resume":
                data.setdefault("paused_users", {}).pop(uid, None)  
                json.dump(data, open("memory.json","w"))
            elif action == "reply":
                reply = request.form.get("reply")
            if reply:
                send_whatsapp_reply(uid, reply)
                memory.add_message(uid, "model", reply,source="OWNER")
                data.setdefault("paused_users", {})[uid] = True 
                json.dump(data, open("memory.json","w"))
            return redirect(f"/admin/chat/{uid}?p={ADMIN_PASSWORD}")
    
        data = json.load(open("memory.json")) if os.path.exists("memory.json") else {"chats":{}}
        msgs = data.get("chats",{}).get(uid, [])
        profiles = data.get("profiles",{})
        return render_template_string(ADMIN_HTML, uid=uid, msgs=msgs, profiles=profiles, pwd=ADMIN_PASSWORD)
