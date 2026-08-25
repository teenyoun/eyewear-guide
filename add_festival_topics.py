"""Append high-commercial-intent festival topics to content-queue.json."""
import json
from pathlib import Path

BASE = Path(__file__).parent
QP = BASE / "content-queue.json"
queue = json.loads(QP.read_text(encoding="utf-8"))

NEW = [
    {
        "title": "Amazon Prime Day Glasses Deals 2026 — What to Buy and Skip",
        "meta_description": "Prime Day is the best window to buy glasses online. Which deals are real, which are fake markdowns, and what to add to your cart before the clock runs out.",
        "category": "Shopping Guide",
        "read_time": "6 min read",
        "status": "pending",
    },
    {
        "title": "Best Gifts for Glasses Wearers — 2026 Holiday Gift Guide",
        "meta_description": "From premium cases to lens care kits and stylish frames — 20+ gift ideas for the glasses wearer in your life, sorted by budget.",
        "category": "Gift Guide",
        "read_time": "7 min read",
        "status": "pending",
    },
    {
        "title": "Best Sunglasses Under $50 on Amazon — 2026 Deals Edition",
        "meta_description": "Polarized, stylish and under $50: the best-value sunglasses on Amazon right now, compared on UV protection, build quality and style.",
        "category": "Sunglasses",
        "read_time": "5 min read",
        "status": "pending",
    },
    {
        "title": "Black Friday Glasses Deals 2026 — What to Expect and How to Prepare",
        "meta_description": "Black Friday predictions for glasses, contacts and eye care: which retailers discount, when deals drop, and how to avoid fake sales.",
        "category": "Shopping Guide",
        "read_time": "5 min read",
        "status": "pending",
    },
    {
        "title": "Best Prescription Sports Glasses on Amazon — Tested Picks",
        "meta_description": "Play sports with clear vision: impact-rated prescription glasses for basketball, cycling, tennis and more, with lens and frame recommendations.",
        "category": "Prescription Glasses",
        "read_time": "6 min read",
        "status": "pending",
    },
    {
        "title": "Glasses Accessories Gift Guide — Cases, Clips, Cleaners and More",
        "meta_description": "Small gifts that every glasses wearer actually needs: hard cases, sunglass clips, lens cleaning kits, straps and stands — all under $30.",
        "category": "Gift Guide",
        "read_time": "5 min read",
        "status": "pending",
    },
]

existing_titles = {q.get("title") for q in queue}
added = 0
for n in NEW:
    if n["title"] not in existing_titles:
        queue.append(n)
        added += 1
        existing_titles.add(n["title"])

QP.write_text(json.dumps(queue, ensure_ascii=False, indent=1), encoding="utf-8")
pending = sum(1 for q in queue if q.get("status") == "pending")
print(f"Added {added} topics. Queue total: {len(queue)}, pending: {pending}")
