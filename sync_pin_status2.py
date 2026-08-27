"""Sync pins-queue.json: mark pins published by title keyword match."""
import json
from pathlib import Path

p = Path("pins-queue.json")
q = json.loads(p.read_text(encoding="utf-8"))

keywords = ("Online Glasses Stores", "Headaches")
n = 0
for i in q:
    t = i.get("title", "")
    if any(k in t for k in keywords) and i.get("status") == "pending":
        i["status"] = "published"
        n += 1

p.write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding="utf-8")
pending = [i["title"] for i in q if i.get("status") == "pending"]
print(f"marked: {n}. remaining pending: {len(pending)}")
for t in pending:
    print("  -", t)
