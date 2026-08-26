"""Sync pins-queue.json: mark already-published pins as published."""
import json
from pathlib import Path

p = Path("pins-queue.json")
q = json.loads(p.read_text(encoding="utf-8"))

published_images = {"pin-01-cheap-sunglasses.jpg", "pin-02-blue-light.jpg",
                    "pin-03-reading-women.jpg", "pin-04-frame-materials.jpg"}
updated = 0
for item in q:
    name = Path(item.get("image", "")).name if item.get("image") else ""
    if name in published_images and item.get("status") == "pending":
        item["status"] = "published"
        updated += 1

p.write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding="utf-8")
pending = [i["title"] for i in q if i.get("status") == "pending"]
print(f"Marked published: {updated}. Remaining pending: {len(pending)}")
for t in pending:
    print("  -", t)
