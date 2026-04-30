"""
parser.py — Member B
Core logic: converts classified lines → structured MCQ list → saves mcq_bank.json

Public API (called by Member C):
    from parser import process_lines
    mcqs = process_lines(lines)        # lines = list[str] from Member A
"""

import re
import json
import os
from classifier import normalize_line, classify_lines


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

OPTION_LABEL_RE = re.compile(r'^[a-d]\)\s*', re.IGNORECASE)
QUESTION_NUM_RE = re.compile(r'^\d+[\.\)]\s*')


def strip_option_label(text: str) -> str:
    """Remove 'a) ', 'b) ' … prefix and return the clean option text."""
    return OPTION_LABEL_RE.sub('', text).strip()


def strip_question_number(text: str) -> str:
    """Remove leading '1. ', '2) ' … and return the clean question text."""
    return QUESTION_NUM_RE.sub('', text).strip()


def looks_like_new_question(norm_line: str, label: str) -> bool:
    """True when this line should start a fresh MCQ block."""
    return label == 'question'


# ─────────────────────────────────────────────
#  Core parser
# ─────────────────────────────────────────────

def parse_classified(classified: list[tuple[str, str]]) -> list[dict]:
    """
    Walk through (line, label) pairs and group them into MCQ objects.

    Handles:
      • multi-line questions (consecutive 'question' labels)
      • options without labels (plain text after a question)
      • noise lines scattered anywhere
      • incomplete MCQs (< 2 options) → rejected
    """
    mcqs: list[dict] = []
    current_question_parts: list[str] = []
    current_options: list[str] = []
    in_block = False  # True once we've seen the first question

    def flush(q_parts, opts):
        """Build one MCQ dict; return None if it's invalid."""
        question_text = ' '.join(q_parts).strip()
        question_text = strip_question_number(question_text)
        if not question_text:
            return None
        if len(opts) < 4:
            return None
        return {
            'question': question_text,
            'options': opts,
        }

    for norm, label in classified:
        if label == 'noise':
            # Noise is silently dropped; never interrupts a block
            continue

        if label == 'question':
            if in_block and not current_options and not QUESTION_NUM_RE.match(norm):
                # Continuation of question text (no options seen yet)
                current_question_parts.append(norm)
            else:
                # Save previous block before starting a new one
                if in_block:
                    mcq = flush(current_question_parts, current_options)
                    if mcq:
                        mcqs.append(mcq)
                # Start new block
                current_question_parts = [norm]
                current_options = []
                in_block = True

        elif label == 'option':
            if not in_block:
                # Orphan option with no leading question — skip
                continue
            option_text = strip_option_label(norm)
            if option_text:
                current_options.append(option_text)

    # Don't forget the last block
    if in_block:
        mcq = flush(current_question_parts, current_options)
        if mcq:
            mcqs.append(mcq)

    return mcqs


def assign_ids(mcqs: list[dict]) -> list[dict]:
    """Add sequential 'id' fields starting from 1."""
    for i, mcq in enumerate(mcqs, start=1):
        mcq['id'] = i
    # Reorder keys for readability: id, question, options
    return [{'id': m['id'], 'question': m['question'], 'options': m['options']} for m in mcqs]


# ─────────────────────────────────────────────
#  Public API — what Member C imports
# ─────────────────────────────────────────────

def process_lines(lines: list[str]) -> list[dict]:
    """
    Full pipeline:
      list[str]  →  normalize  →  classify  →  parse  →  assign IDs
                →  list of valid MCQ dicts

    Usage:
        from parser import process_lines
        mcqs = process_lines(lines)
    """
    if not lines:
        return []

    classified = classify_lines(lines)
    raw_mcqs = parse_classified(classified)
    mcqs = assign_ids(raw_mcqs)
    return mcqs


# ─────────────────────────────────────────────
#  JSON output helper
# ─────────────────────────────────────────────

def save_mcq_bank(mcqs: list[dict], path: str = 'data/mcq_bank.json') -> None:
    """Write MCQs to JSON file. Creates parent directories if needed."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(mcqs, f, indent=2, ensure_ascii=False)
    print(f"[parser] Saved {len(mcqs)} MCQs → {path}")


# ─────────────────────────────────────────────
#  Standalone test / demo
# ─────────────────────────────────────────────

DEMO_INPUT: list[str] = [
    # Block 1 — clean
    "1. What is RAM?",
    "a) Memory",
    "b) CPU",
    "c) Storage",
    "d) Processor",
    # Block 2 — messy OCR
    "2.Which of the following is an output device",   # no ?
    "A. Monitor",
    "B.Keyboard",
    "C ) Mouse",
    "D)Printer",
    # Noise in the middle
    "Page 2",
    "Total Marks: 50",
    # Block 3 — numbered with )
    "3) Define an operating system",
    "a) Software that manages hardware",
    "b) A type of RAM",
    "c) A network protocol",
    # Block 4 — multi-line question
    "4. Which data structure uses",
    "LIFO order?",              # continuation of question (will be noise-labelled but…)
    "a) Queue",
    "b) Stack",
    "c) Array",
    "d) Tree",
    # Block 5 — too few options (should be REJECTED)
    "5. What is an algorithm?",
    "a) A step-by-step procedure",
    # Block 6 — option labels missing
    "6. What does CPU stand for?",
    "Central Processing Unit",
    "Control Processing Unit",
    "Core Processing Unit",
    # Block 7 — numbers with mixed style
    "7. What is the full form of HTTP?",
    "a ) HyperText Transfer Protocol",
    "b ) HyperText Transmission Protocol",
    "c ) High Transfer Text Protocol",
    "d ) HyperText Transport Protocol",
    # Block 8 — garbage surrounding a valid block
    "Instructions: Attempt all questions",
    "8. Which language is used for web pages?",
    "a) HTML",
    "b) Python",
    "c) Java",
    "d) C++",
    "Name: ___________",
    # Block 9
    "9. What is the binary representation of 5?",
    "a) 101",
    "b) 110",
    "c) 011",
    "d) 111",
    # Block 10 — no label options
    "10. Which is not a programming language?",
    "Python",
    "HTML",
    "Microsoft Word",
    "Java",
]


if __name__ == '__main__':
    print("=" * 55)
    print("  Member B — Parser Demo")
    print("=" * 55)

    mcqs = process_lines(DEMO_INPUT)

    print(f"\n✅ Extracted {len(mcqs)} valid MCQs:\n")
    for mcq in mcqs:
        print(f"  [{mcq['id']}] {mcq['question']}")
        for opt in mcq['options']:
            print(f"       • {opt}")
        print()

    save_mcq_bank(mcqs, path='data/mcq_bank.json')

    # Also pretty-print JSON to console
    print("\n── JSON preview (first 2 MCQs) ──")
    print(json.dumps(mcqs[:2], indent=2))
