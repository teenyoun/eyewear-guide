"""Rebuild content-queue.json pending order: insert regular topics for September,
push festival content (Prime Day / Black Friday / Holiday) to the right timing.
Keeps published entries untouched; preserves fields of existing entries.
"""
import json
from pathlib import Path

BASE = Path(__file__).parent
QP = BASE / "content-queue.json"
queue = json.loads(QP.read_text(encoding="utf-8"))

pending = [i for i in queue if i.get("status") == "pending"]
done = [i for i in queue if i.get("status") != "pending"]

# New regular topics to insert for Sept 1-20
NEW_TOPICS = [
    {"title": "Polarized vs Non-Polarized Sunglasses — What's the Real Difference",
     "meta_description": "Polarized lenses cut glare but cost more and can distort LCD screens. When they're worth it and when plain UV400 is enough.",
     "category": "sunglasses"},
    {"title": "Best Prescription Sunglasses on Amazon — Tested and Compared",
     "meta_description": "Prescription sunglasses from $40 to $300: lens options, tint choices, and which stores offer the best value in 2026.",
     "category": "buying-guide"},
    {"title": "How to Measure Your Face for Glasses at Home — 3 Easy Methods",
     "meta_description": "Get the right frame width without visiting a store: credit card method, ruler method, and pupil distance explained.",
     "category": "how-to"},
    {"title": "Best Glasses for Round Faces — Framing Soft Features",
     "meta_description": "Angular, rectangular and geometric frames add definition to round faces. Shape guide with what to avoid.",
     "category": "face-shape"},
    {"title": "Best Sunglasses for Oval Faces — The Style That Suits Everyone",
     "meta_description": "Oval faces suit nearly every frame. The 2026 picks that flatter best plus proportion rules.",
     "category": "face-shape"},
    {"title": "Best Safety Glasses for Woodworking — Protect Your Eyes on the Job",
     "meta_description": "Impact-rated safety glasses with anti-fog, side shields and good vision. What ANSI Z87.1 really means.",
     "category": "safety"},
    {"title": "How to Clean Glasses Properly — Stop Scratching Your Lenses",
     "meta_description": "The microfiber vs t-shirt mistake everyone makes, and the correct 4-step lens cleaning routine.",
     "category": "how-to"},
    {"title": "Best Glasses for Square Faces — Softening Strong Jawlines",
     "meta_description": "Round, oval and aviator frames soften square jawlines. Frame width and browline tips included.",
     "category": "face-shape"},
    {"title": "Best Sports Sunglasses for Running — Stay Cool and See Clearly",
     "meta_description": "Lightweight, sweat-proof running sunglasses with good coverage. Rubber nose grips and vented lenses compared.",
     "category": "sports"},
]

# Map existing pending titles to their desired positions in the new order
def find(title_key):
    for p in pending:
        if title_key.lower() in p.get("title", "").lower():
            return p
    return None

# Build ordered list: regular topics first (Sept), festival topics at right timing
ordered = []
# 1. Sept 1: best prescription sunglasses (NEW)
ordered.append(NEW_TOPICS[1])
# 2. Sept 2: polarized vs non-polarized (NEW)
ordered.append(NEW_TOPICS[0])
# 3. Women Over 50 (existing)
ordered.append(find("Women Over 50"))
# 4. measure face (NEW)
ordered.append(NEW_TOPICS[2])
# 5. round faces (NEW)
ordered.append(NEW_TOPICS[3])
# 6. oval faces (NEW)
ordered.append(NEW_TOPICS[4])
# 7. safety glasses woodworking (NEW)
ordered.append(NEW_TOPICS[5])
# 8. clean glasses properly (NEW)
ordered.append(NEW_TOPICS[6])
# 9. square faces (NEW)
ordered.append(NEW_TOPICS[7])
# 10. sports sunglasses running (NEW)
ordered.append(NEW_TOPICS[8])
# 11. sunglasses under $50 (existing, high-intent)
ordered.append(find("Sunglasses Under $50"))
# 12. prescription sports glasses (existing, high-intent)
ordered.append(find("Prescription Sports Glasses"))
# 13. late Sept: Prime Day deals (2-3 weeks before mid-Oct Prime Day)
ordered.append(find("Prime Day"))
# 14. early Nov: Black Friday preview
ordered.append(find("Black Friday"))
# 15. late Nov: gift guide
ordered.append(find("Gifts for Glasses Wearers"))
# 16. late Nov: accessories gift guide
ordered.append(find("Accessories Gift Guide"))

# Remove any existing pending topics that were not placed above (should not happen)
placed_ids = {id(i) for i in ordered if i is not None}
missing = [p for p in pending if id(p) not in placed_ids]
ordered = [i for i in ordered if i is not None] + missing

new_queue = done + ordered
QP.write_text(json.dumps(new_queue, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Total: {len(new_queue)} (done {len(done)} + pending {len(ordered)})")
print("New pending order:")
for i, t in enumerate(ordered, 1):
    print(f"  {i:2d}. {t['title']}")
