import os
from OCR import extract_text
from preprocessing import preprocess
from mcq_parser import process_lines, save_mcq_bank
from quiz import load_questions, run_quiz

MCQ_BANK_PATH = "data/mcq_bank.json"

def main():
    print("\n" + "="*50)
    print("   MCQ Extractor & Quiz Generator")
    print("="*50)

    image_path = input("\n📸 Enter path to question paper image: ").strip()

    if not os.path.exists(image_path):
        print(f"❌ File not found: {image_path}")
        return

    # STEP 2: OCR
    print("\n🔍 Extracting text from image...")
    raw_lines = extract_text(image_path)
    print(f"✅ Extracted {len(raw_lines)} raw lines")

    # STEP 3: Preprocess
    print("\n🧹 Preprocessing text...")
    clean_lines = preprocess(raw_lines)
    print(f"✅ {len(clean_lines)} clean lines after preprocessing")

    # STEP 4 & 5: Classify + Parse
    print("\n🧠 Detecting MCQs...")
    mcqs = process_lines(clean_lines)

    if mcqs:
        print(f"✅ {len(mcqs)} MCQs extracted!")
        save_mcq_bank(mcqs, MCQ_BANK_PATH)
    else:
        print("⚠️  No MCQs detected from image (complex layout).")
        print("📂 Loading questions from existing bank instead...")

    # STEP 6: Run Quiz
    print("\n🎲 Starting Quiz...")
    questions = load_questions(MCQ_BANK_PATH)
    print(f"✅ {len(questions)} questions loaded!")
    run_quiz(questions)

if __name__ == "__main__":
    main()