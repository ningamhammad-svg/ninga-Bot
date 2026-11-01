
import json, os
from collections import OrderedDict

FILE = "memory.json"
chat = {}
profiles = {}
paused_users = {}
seen = OrderedDict()

# Soma file na vitu vyote 3
if os.path.exists(FILE):
    try:
        data = json.load(open(FILE, "r", encoding="utf-8"))
        chat = data.get("chats", {})
        profiles = data.get("profiles", {})
        paused_users = data.get("paused_users", {})
    except:
        chat = {}
        profiles = {}
        paused_users = {}

def save():
    # Muhimu: Save vitu vyote 3, sio chats tu
    json.dump({
        "chats": chat, 
        "profiles": profiles, 
        "paused_users": paused_users
    }, open(FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def is_dup(mid):
    if mid in seen: return True
    seen[mid] = 1
    if len(seen) > 200:
        seen.popitem(0)
    return False

def get_history(uid):
    # Rudisha message zote kwa AI, sio 10 tu
    return chat.get(uid, [])[-15:]

def add(uid, role, text, source="BOT"):
    chat.setdefault(uid, []).append({
        "role": role, 
        "text": text, 
        "source": source,
        "time": __import__("time").time()
    })
    # Usikate hadi 10, acha hadi 100 ili General ionekane
    chat[uid] = chat[uid][-100:]
    save()

def get_all_chats():
    return chat

def pause_user(uid):
    paused_users[uid] = True
    save()

def unpause_user(uid):
    paused_users.pop(uid, None)
    save()

# Hii ndio object ambayo ninga.py inaita
memory = type("", (), {
    "is_duplicate": staticmethod(is_dup),
    "get_history": staticmethod(get_history),
    "add_message": staticmethod(add),
    "get_all_chats": staticmethod(get_all_chats),
    "pause_user": staticmethod(pause_user),
    "unpause_user": staticmethod(unpause_user),
    "chats": chat,
    "paused_users": paused_users
})
