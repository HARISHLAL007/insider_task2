"""
classifier.py — Member B
Rule-based classifier: labels each line as 'question', 'option', or 'noise'
"""

import re


# ─────────────────────────────────────────────
#  Normaliser  (fix OCR mess before classifying)
# ─────────────────────────────────────────────

def normalize_line(line: str) -> str:
    """
    Fix common OCR artefacts so the classifier sees clean text.
    Examples handled:
        "1.What is RAM"  →  "1. What is RAM"
        "a ) Memory"     →  "a) Memory"
        "A.Memory"       →  "a) Memory"
        "1)What..."      →  "1. What..."
    """
    line = line.strip()
    if not line:
        return line

    # Collapse multiple spaces
    line = re.sub(r' {2,}', ' ', line)

    # Normalise option labels: "a )", "a.", "A)", "A." → "a)"
    line = re.sub(
        r'^([a-dA-D])\s*[\.\)]\s*',
        lambda m: m.group(1).lower() + ') ',
        line
    )

    # Normalise question numbers: "1.What" → "1. What"
    line = re.sub(r'^(\d+)\.\s*', lambda m: m.group(1) + '. ', line)

    # "1)What" → "1. What"
    line = re.sub(r'^(\d+)\)\s*', lambda m: m.group(1) + '. ', line)

    return line


# ─────────────────────────────────────────────
#  Classifier
# ─────────────────────────────────────────────

QUESTION_NUMBER_RE = re.compile(r'^\d+[\.\)]\s')
OPTION_RE = re.compile(r'^[a-d]\)\s', re.IGNORECASE)
NOISE_TOKENS = {
    'page', 'section', 'instructions', 'note', 'answer', 'name', 'date',
    'roll', 'marks', 'time', 'class', 'subject', 'total', 'signature'
}


def classify(line: str) -> str:
    """
    Return one of: 'question' | 'option' | 'noise'

    Strategy (ordered, first match wins):
      1. Empty or too-short  → noise
      2. Noise keyword match → noise
      3. Starts with option label (a) b) c) d)) → option
      4. Starts with a number prefix (1. 2. 3.) → question
      5. Ends with '?'  → question
      6. Contains typical question words → question
      7. Fallback → noise
    """
    norm = normalize_line(line)

    if not norm or len(norm) < 3:
        return 'noise'

    lower = norm.lower()

    # 1. Known noise keywords at the start
    first_word = lower.split()[0].strip('.:,')
    if first_word in NOISE_TOKENS:
        return 'noise'

    # 2. Option label
    if OPTION_RE.match(norm):
        return 'option'

    # 3. Numbered question
    if QUESTION_NUMBER_RE.match(norm):
        return 'question'

    # 4. Ends with question mark
    if norm.rstrip().endswith('?'):
        return 'question'

    # 5. Contains typical question starters
    question_starters = (
        'what', 'which', 'who', 'where', 'when', 'why', 'how',
        'define', 'explain', 'describe', 'find', 'calculate',
        'state', 'list', 'name', 'give', 'write'
    )
    if any(lower.startswith(w) for w in question_starters):
        return 'question'

    return 'noise'


# ─────────────────────────────────────────────
#  Batch helper
# ─────────────────────────────────────────────

def classify_lines(lines: list[str]) -> list[tuple[str, str]]:
    """
    Returns list of (normalized_line, label) pairs.
    Skips blank lines entirely.
    """
    results = []
    for raw in lines:
        norm = normalize_line(raw)
        if norm:
            label = classify(norm)
            results.append((norm, label))
    return results


# ─────────────────────────────────────────────
#  Quick test
# ─────────────────────────────────────────────

if __name__ == '__main__':
    sample = [
        "1.What is RAM?",
        "a ) Memory",
        "b)CPU",
        "c) Storage",
        "Some garbage text here",
        "2. Which of the following is an output device?",
        "A. Monitor",
        "B. Keyboard",
        "C.Mouse",
        "D) Printer",
        "Page 1 of 3",
        "3) Define an operating system",
        "a) Software that manages hardware",
        "b) A type of hardware",
    ]

    for raw in sample:
        norm = normalize_line(raw)
        label = classify(norm)
        print(f"  [{label:8}]  {norm}")
