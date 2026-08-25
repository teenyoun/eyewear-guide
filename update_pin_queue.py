"""Update pins-queue.json: fix old-domain links, append new batch pins."""
import json
from pathlib import Path

BASE = Path(__file__).parent
QP = BASE / "pins-queue.json"
queue = json.loads(QP.read_text(encoding="utf-8"))

# 1. Fix old domain links
fixed = 0
for p in queue:
    if "teenyoun.github.io" in p.get("link", ""):
        p["link"] = p["link"].replace("https://teenyoun.github.io/eyewear-guide", "https://glasses.teenyoun.com")
        fixed += 1
print(f"Fixed old-domain links: {fixed}")

# 2. New batch pins (local images, published in order over coming days)
NEW = [
    {
        "title": "Best Cheap Sunglasses on Amazon Under $25 — Style on a Budget",
        "description": "Trendy wayfarers, aviators and retro frames that look $100+ but cost under $25. Our top Amazon picks under $25 for 2026.",
        "link": "https://glasses.teenyoun.com/articles/best-cheap-sunglasses-on-amazon-under-25-style-on-a-budget.html",
        "image": "pins-batch/pin-01-cheap-sunglasses.jpg",
        "status": "pending",
    },
    {
        "title": "Do Blue Light Glasses Work? The Science-Based Answer",
        "description": "We reviewed peer-reviewed studies. Evidence for sleep improvement is solid; for eye strain, less so. Honest 2026 breakdown.",
        "link": "https://glasses.teenyoun.com/articles/do-blue-light-glasses-work.html",
        "image": "pins-batch/pin-02-blue-light.jpg",
        "status": "pending",
    },
    {
        "title": "Best Reading Glasses for Women — Stylish & Comfortable",
        "description": "Cat-eye, oversized and minimalist readers that don't look like reading glasses. Fashion meets function for women over 40.",
        "link": "https://glasses.teenyoun.com/articles/best-reading-glasses-women.html",
        "image": "pins-batch/pin-03-reading-women.jpg",
        "status": "pending",
    },
    {
        "title": "Titanium vs Acetate vs TR90 — Glasses Frame Materials Compared",
        "description": "Weight, durability, hypoallergenic properties and price compared. Which frame material is right for your lifestyle?",
        "link": "https://glasses.teenyoun.com/articles/titanium-vs-acetate-vs-tr90-glasses-frames-material-guide.html",
        "image": "pins-batch/pin-04-frame-materials.jpg",
        "status": "pending",
    },
    {
        "title": "Best Sunglasses for Driving — Polarized Picks That Cut Glare",
        "description": "Glare, dashboard reflections and tunnel transitions — the lenses that make driving safer and more comfortable.",
        "link": "https://glasses.teenyoun.com/articles/best-sunglasses-for-driving.html",
        "image": "pins-batch/pin-05-driving.jpg",
        "status": "pending",
    },
    {
        "title": "Transition Lenses Review 2026 — Are Gen 8 Worth the Upgrade?",
        "description": "Darkening speed, tint quality, durability and price — we tested photochromic lenses so you don't have to. Full review.",
        "link": "https://glasses.teenyoun.com/articles/transition-lenses-review-2026-are-gen-8-worth-the-upgrade-.html",
        "image": "pins-batch/pin-06-transitions.jpg",
        "status": "pending",
    },
]
queue.extend(NEW)
QP.write_text(json.dumps(queue, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Queue now has {len(queue)} pins ({sum(1 for p in queue if p['status']=='pending')} pending)")
