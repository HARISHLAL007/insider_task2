import os
import logging
from OCR import extract_text
from preprocessing import preprocess
from mcq_parser import process_lines, save_mcq_bank
from quiz import load_questions, run_quiz

MCQ_BANK_PATH = "data/mcq_bank.json"

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("\n" + "="*50)
    print("   MCQ Extractor & Quiz Generator")
    print("="*50)

    image_path = input("\nEnter path to question paper image: ").strip()

    if not os.path.exists(image_path):
        print(f"Error: File not found: {image_path}")
        return

    # STEP 2: OCR
    print("\nExtracting text from image... (This may take a minute or two, please wait!)")
    logging.info(f"Starting OCR on {image_path}")
    raw_lines = extract_text(image_path)
    logging.info(f"OCR completed, found {len(raw_lines)} lines")
    print(f"Extracted {len(raw_lines)} raw lines")

    # STEP 3: Preprocess
    print("\nPreprocessing text...")
    logging.info("Starting text preprocessing")
    clean_lines = preprocess(raw_lines)
    logging.info("Preprocessing completed")
    print(f"{len(clean_lines)} clean lines after preprocessing")

    # STEP 4 & 5: Classify + Parse
    print("\nDetecting MCQs...")
    logging.info("Starting MCQ parsing")
    mcqs = process_lines(clean_lines)

    if mcqs:
        print(f"{len(mcqs)} MCQs extracted!")
        logging.info(f"Extracted {len(mcqs)} MCQs")
        save_mcq_bank(mcqs, MCQ_BANK_PATH)
    else:
        print("No MCQs detected from image (complex layout).")
        print("Loading questions from existing bank instead...")

    # STEP 6: Run Quiz
    print("\nStarting Quiz...")
    questions = load_questions(MCQ_BANK_PATH)
    print(f"{len(questions)} questions loaded!")
    run_quiz(questions)

if __name__ == "__main__":
    main()