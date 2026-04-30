import json

with open('data/mcq_bank.json', encoding='utf-8') as f:
    bank = json.load(f)

# Stamp source on questions from finallytesting.jpg (IDs 1-13, no source yet)
for q in bank:
    if 'source' not in q:
        q['source'] = 'finallytesting.jpg'

with open('data/mcq_bank.json', 'w', encoding='utf-8') as f:
    json.dump(bank, f, indent=2, ensure_ascii=False)

print(f'Done. {len(bank)} questions in bank:')
for q in bank:
    qid = q["id"]
    src = q["source"]
    qtxt = q["question"][:55]
    print(f'  [{qid:2d}] [{src}] {qtxt}')
