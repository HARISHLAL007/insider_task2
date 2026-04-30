import json
import random
import os
import sys

def load_questions(filepath="data/mcq_bank.json"):
    if not os.path.exists(filepath):
        print(f"Error: Question bank not found at {filepath}")
        sys.exit(1)
    with open(filepath, "r") as f:
        questions = json.load(f)
    return questions

def run_quiz(questions):
    # Only use questions with exactly 4 options
    valid_questions = [q for q in questions if len(q.get("options", [])) == 4]

    if not valid_questions:
        print("Error: No valid questions found in the bank (need 4 options each).")
        return

    # Pick up to 10 random questions
    selected = random.sample(valid_questions, min(10, len(valid_questions)))
    score = 0
    total = len(selected)

    print("\n" + "="*50)
    print("        Welcome to the MCQ Quiz!")
    print("="*50)
    print(f"  {total} questions | Type a, b, c, or d\n")

    for i, mcq in enumerate(selected):
        source = mcq.get("source", "unknown")
        print(f"Q{i+1}. [{source}] {mcq['question']}")

        # Track correct answer BEFORE shuffling
        correct_answer = mcq["options"][0]

        # Shuffle options
        options = mcq["options"].copy()
        random.shuffle(options)

        # Display options — only as many as exist
        all_labels = ["a", "b", "c", "d"]
        labels = all_labels[:len(options)]
        label_prompt = "/".join(labels)
        for label, option in zip(labels, options):
            print(f"   {label}) {option}")

        # Get answer — only allow valid labels for this question
        while True:
            answer = input(f"\n   Your answer ({label_prompt}): ").strip().lower()
            if answer in labels:
                break
            print(f"   Invalid input. Please enter {label_prompt}.")

        # Check answer
        idx = labels.index(answer)
        chosen_answer = options[idx]

        if chosen_answer == correct_answer:
            print("   Correct!\n")
            score += 1
        else:
            print(f"   Wrong! Correct answer: {correct_answer}\n")

        print("-"*50)

    # Final score
    print(f"\nQuiz Complete! Your Score: {score}/{total}")
    percentage = (score / total) * 100
    print(f"   Percentage: {percentage:.1f}%")

    if percentage >= 80:
        print("   Excellent!")
    elif percentage >= 60:
        print("   Good job!")
    else:
        print("   Keep practicing!")

    print("="*50 + "\n")

if __name__ == "__main__":
    questions = load_questions()
    run_quiz(questions)