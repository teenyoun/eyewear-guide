import json, sys, io

# Merge batch3.json into content-queue.json
with open('content-queue.json', 'r', encoding='utf-8') as f:
    queue = json.load(f)

with open('batch3.json', 'r', encoding='utf-8') as f:
    batch = json.load(f)

queue.extend(batch)

with open('content-queue.json', 'w', encoding='utf-8') as f:
    json.dump(queue, f, indent=2, ensure_ascii=False)

pending = [q for q in queue if q.get('status') == 'pending']
print(f'Total queue: {len(queue)} items')
print(f'Pending: {len(pending)}')
for p in pending:
    print(' -', p['title'][:60])
