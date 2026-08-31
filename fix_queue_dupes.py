"""Remove duplicate-topic entries from content-queue.json and insert fresh topics."""
import json
from pathlib import Path

BASE = Path(__file__).parent
QP = BASE / "content-queue.json"
queue = json.loads(QP.read_text(encoding="utf-8"))

DUP_MARKERS = [
    "Prescription Sunglasses on Amazon",
    "Polarized vs Non-Polarized",
    "Round Faces",
    "Sunglasses for Oval Faces",
    "Clean Glasses Properly",
    "Square Faces",
]

NEW_TOPICS = [
    {"title": "Best Glasses for Diamond Faces — Framing High Cheekbones",
     "meta_description": "Diamond faces have narrow foreheads and strong cheekbones. Oval, cat-eye and rimless frames balance the proportions.",
     "category": "face-shape"},
    {"title": "Progressive Lens Adaptation — Week-by-Week Adjustment Guide",
     "meta_description": "Most people adapt to progressives in 1-2 weeks. The common mistakes, head movement techniques, and when to return them.",
     "category": "lenses"},
    {"title": "How to Read Your Glasses Prescription — OD, OS, SPH, CYL Explained",
     "meta_description": "Decode your prescription in 5 minutes: sphere, cylinder, axis, prism and PD — what every number means and when to worry.",
     "category": "education"},
    {"title": "Night Driving Glasses — Do Yellow Lenses Actually Help?",
     "meta_description": "Yellow-tinted night driving glasses: the science says they don't improve visibility, but anti-glare AR coating does. 2026 verdict.",
     "category": "sunglasses"},
    {"title": "Best Eyeglass Frames for Men — 2026 Style Guide",
     "meta_description": "From wayfarers to rimless: the frame shapes and materials that suit men's faces in 2026, at every price point.",
     "category": "buying-guide"},
    {"title": "Best Sunglasses for Kids — UV Protection They'll Actually Wear",
     "meta_description": "Kids need real UV400 protection, not toys. Durable, flexible frames and lenses that survive the playground. 2026 picks.",
     "category": "kids"},
    {"title": "Glasses vs Contacts for Sports — What Athletes Actually Wear",
     "meta_description": "Prescription goggles, sports glasses or contacts for training and games? Impact risk, sweat, and vision field compared.",
     "category": "sports"},
    {"title": "Best Women's Sunglasses 2026 — Classic to Trendy",
     "meta_description": "The sunglasses silhouettes dominating 2026: oversized, geometric, retro cat-eye — and which shapes suit which face.",
     "category": "sunglasses"},
]

# Archive duplicate-pending entries
archived = 0
remaining = []
for i in queue:
    t = i.get("title", "")
    if any(m in t for m in DUP_MARKERS) and i.get("status") == "pending":
        i["status"] = "archived"
        i["archived_reason"] = "duplicate of existing article"
        archived += 1
    remaining.append(i)

# Insert new topics right before the $50 / festival block (position of 'Sunglasses Under $50')
insert_at = None
for idx, i in enumerate(remaining):
    if "Sunglasses Under $50" in i.get("title", "") and i.get("status") == "pending":
        insert_at = idx
        break
if insert_at is None:
    insert_at = len(remaining)

new_queue = remaining[:insert_at] + NEW_TOPICS + remaining[insert_at:]
QP.write_text(json.dumps(new_queue, ensure_ascii=False, indent=1), encoding="utf-8")

pend = [i["title"] for i in new_queue if i.get("status") == "pending"]
print(f"archived duplicates: {archived}, new topics added: {len(NEW_TOPICS)}")
print(f"pending total: {len(pend)}")
for idx, t in enumerate(pend, 1):
    print(f"  {idx:2d}. {t}")
