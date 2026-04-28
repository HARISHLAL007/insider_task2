import json
import random

def load_questions(filepath="data/mcq_bank.json"):
    with open(filepath, "r") as f:
        questions = json.load(f)
    return questions

def run_quiz(questions):
    # Pick up to 10 random questions
    selected = random.sample(questions, min(10, len(questions)))
    score = 0
    total = len(selected)

    print("\n" + "="*50)
    print("        Welcome to the MCQ Quiz!")
    print("="*50)
    print(f"  {total} questions | Type a, b, c, or d\n")

    for i, mcq in enumerate(selected):
        print(f"Q{i+1}. {mcq['question']}")

        # Shuffle options
        options = mcq["options"].copy()
        random.shuffle(options)

        # Display options
        labels = ["a", "b", "c", "d"]
        for label, option in zip(labels, options):
            print(f"   {label}) {option}")

        # Get answer
        while True:
            answer = input("\n   Your answer (a/b/c/d): ").strip().lower()
            if answer in labels:
                break
            print("   Invalid input. Please enter a, b, c, or d.")

        # Check answer (first option in original list is always correct)
        correct_answer = mcq["options"][0]
        chosen_answer = options[labels.index(answer)]

        if chosen_answer == correct_answer:
            print("   ✅ Correct!\n")
            score += 1
        else:
            print(f"   ❌ Wrong! Correct answer: {correct_answer}\n")

        print("-"*50)

    # Final score
    print(f"\n🎯 Quiz Complete! Your Score: {score}/{total}")
    percentage = (score / total) * 100
    print(f"   Percentage: {percentage:.1f}%")

    if percentage >= 80:
        print("   🏆 Excellent!")
    elif percentage >= 60:
        print("   👍 Good job!")
    else:
        print("   📚 Keep practicing!")

    print("="*50 + "\n")

if __name__ == "__main__":
    questions = load_questions()
    run_quiz(questions)