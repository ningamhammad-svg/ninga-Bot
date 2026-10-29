# rememb.py
import json, os
from collections import OrderedDict

FILE = "memory.json"
chat = {}
seen = OrderedDict()

if os.path.exists(FILE):
    try:
        chat = json.load(open(FILE)).get("chats", {})
    except:
        chat = {}

def save():
    json.dump({"chats": chat}, open(FILE, "w"))

def is_dup(mid):
    if mid in seen: return True
    seen[mid] = 1
    if len(seen) > 200: seen.popitem(0)
    return False

def get_history(uid):
    return [{"role": m["role"], "parts": m["parts"]} for m in chat.get(uid, [])][-10:]

def add(uid, role, text):
    chat.setdefault(uid, []).append({"role": role, "parts": [text]})
    chat[uid] = chat[uid][-10:]
    save()

memory = type("M", (), {"is_duplicate": staticmethod(is_dup), "get_history": staticmethod(get_history), "add_message": staticmethod(add)})()
