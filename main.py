import os
import json
import logging
from OCR import extract_text
from preprocessing import preprocess
from mcq_parser import process_lines, save_mcq_bank
from quiz import load_questions, run_quiz

MCQ_BANK_PATH = "data/mcq_bank.json"


def load_existing_bank(path):
    """Load existing MCQs from the bank. Returns empty list if file missing or invalid."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def merge_mcqs(existing, new_mcqs, source_image="unknown"):
    """
    Merge new MCQs into existing bank.
    Deduplicates by normalised question text so the same question is never added twice.
    Stamps each new MCQ with a 'source' field tracking which image it came from.
    Re-assigns IDs sequentially after merging.
    """
    existing_questions = {q["question"].strip().lower() for q in existing}
    added = 0
    for mcq in new_mcqs:
        key = mcq["question"].strip().lower()
        if key not in existing_questions:
            mcq["source"] = os.path.basename(source_image)
            existing.append(mcq)
            existing_questions.add(key)
            added += 1
    # Re-assign IDs
    for i, q in enumerate(existing, start=1):
        q["id"] = i
    return existing, added


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    print("\n" + "="*50)
    print("   MCQ Extractor & Quiz Generator")
    print("="*50)

    image_path = input("\nEnter path to question paper image: ").strip()

    if not os.path.exists(image_path):
        print(f"Error: File not found: {image_path}")
        return

    # STEP 1: Load existing bank
    existing_mcqs = load_existing_bank(MCQ_BANK_PATH)
    print(f"\nExisting bank: {len(existing_mcqs)} questions loaded.")

    # STEP 2: OCR
    print("\nExtracting text from image... (This may take a minute or two, please wait!)")
    logging.info(f"Starting OCR on {image_path}")
    raw_lines = extract_text(image_path)
    logging.info(f"OCR completed, found {len(raw_lines)} lines")
    print(f"Extracted {len(raw_lines)} raw lines")

    # STEP 3: Preprocess
    print("\nPreprocessing text...")
    clean_lines = preprocess(raw_lines)
    print(f"{len(clean_lines)} clean lines after preprocessing")

    # STEP 4 & 5: Classify + Parse
    print("\nDetecting MCQs...")
    new_mcqs = process_lines(clean_lines)

    if new_mcqs:
        merged, added = merge_mcqs(existing_mcqs, new_mcqs, source_image=image_path)
        print(f"{len(new_mcqs)} MCQs extracted from image. {added} are new (not duplicates).")
        save_mcq_bank(merged, MCQ_BANK_PATH)
        print(f"Bank now has {len(merged)} questions total.")
    else:
        print("No MCQs detected from image.")
        print("Using existing bank for quiz.")

    # STEP 6: Run Quiz from full combined bank
    print("\nStarting Quiz...")
    questions = load_questions(MCQ_BANK_PATH)
    print(f"{len(questions)} questions in bank. Picking up to 10 for the quiz...")
    run_quiz(questions)


if __name__ == "__main__":
    main()