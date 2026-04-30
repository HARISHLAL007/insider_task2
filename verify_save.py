import json
from OCR import extract_text
from preprocessing import preprocess
from mcq_parser import process_lines, save_mcq_bank

print('Running OCR...')
raw = extract_text('finallytesting.jpg')
print(f'Raw lines: {len(raw)}')
clean = preprocess(raw)
print(f'Clean lines: {len(clean)}')
mcqs = process_lines(clean)
print(f'MCQs found: {len(mcqs)}')
save_mcq_bank(mcqs, 'data/mcq_bank.json')

# Verify file
with open('data/mcq_bank.json', encoding='utf-8') as f:
    saved = json.load(f)
print(f'Verified in file: {len(saved)} MCQs')
for q in saved:
    qid = q["id"]
    nopts = len(q["options"])
    qtxt = q["question"][:60]
    print(f'  [{qid}] opts={nopts} | {qtxt}')
