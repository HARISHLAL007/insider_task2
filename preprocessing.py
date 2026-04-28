import re

NOISE_KEYWORDS = {
    'page', 'instruction', 'instructions', 'name', 'roll',
    'date', 'marks', 'time', 'class', 'subject', 'total',
    'section', 'answer', 'signature', 'note', 'q.', 'q)',
    'department', 'college', 'university', 'exam', 'examination',
    'duration', 'maximum', 'attempt', 'all', 'questions'
}


def unicode_artifacts(line: str) -> str:
    replacements = {
        '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"',
        '\u2013': '-', '\u2014': '-',
        '\u2022': '', '\u00b7': '',
        '\u00a0': ' ',
        '|': 'I',
        '\u2026': '...',
    }
    for src, dst in replacements.items():
        line = line.replace(src, dst)
    return line


def ocr_word_errors(line: str) -> str:
    line = line.replace("0ption", "option")
    line = line.replace("0ptions", "options")

    line = re.sub(r'^([Oo])(\s*[\.\)])', lambda m: '0' + m.group(2), line)

    line = re.sub(r'\brnc\b', 'mc', line)
    line = re.sub(r'\brn\b', 'm', line)

    line = re.sub(r'(?<=[a-z])1(?=[a-z])', 'l', line)

    return line


def option_label(line: str) -> str:
    return re.sub(
        r'^\(?\s*([a-dA-D])\s*[\.\)\-:]?\s*',
        lambda m: m.group(1).lower() + ') ',
        line
    )


def question_number(line: str) -> str:
    line = re.sub(r'^(\d+)\s*[\.\)]\s*', lambda m: m.group(1) + '. ', line)
    line = re.sub(r'^(\d+)\.(\S)', r'\1. \2', line)
    return line


def spacing_around_punctuation(line: str) -> str:
    line = re.sub(r'\?(?=[a-zA-Z])', '? ', line)
    line = re.sub(r':(?=[a-zA-Z])', ': ', line)
    return line


def merged_line(line: str) -> list[str]:
    parts = re.split(r'(?=\b[a-dA-D][\)\.\:])', line)
    final = []
    for part in parts:
        sub = re.split(r'(?<=\w)(?=[a-dA-D]\))', part)
        final.extend(sub)
    return [p.strip() for p in final if len(p.strip()) > 1]


def is_noise(line: str) -> bool:
    lower = line.lower().strip()

    if len(lower) < 3:
        return True

    if not re.search(r'[a-zA-Z0-9]', line):
        return True

    if re.match(r'^[\-_=\*\.~\s]+$', line):
        return True

    if re.search(r'_{3,}', line):
        return True

    if re.match(r'^(.)\1{4,}$', line.strip()):
        return True

    first_word = lower.split()[0].strip('.:,)(')
    if first_word in NOISE_KEYWORDS:
        return True

    if re.match(r'^\d+$', lower):
        return True

    if line == line.upper() and len(line) > 4 and not re.match(r'^[a-dA-D\d]', line):
        return True

    return False


def normalize_line(line: str) -> str:
    line = line.strip()
    if not line:
        return ''

    line = unicode_artifacts(line)
    line = ocr_word_errors(line)
    line = question_number(line)
    line = option_label(line)
    line = spacing_around_punctuation(line)

    line = re.sub(r'\s+', ' ', line)
    return line.strip()


def preprocess(lines: list[str]) -> list[str]:
    clean_lines = []

    for raw in lines:
        if not raw or not raw.strip():
            continue

        line = normalize_line(raw)
        if not line:
            continue

        if is_noise(line):
            continue

        split_lines = merged_line(line)
        clean_lines.extend(split_lines)

    return clean_lines
