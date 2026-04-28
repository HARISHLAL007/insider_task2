# MCQ Extractor & Quiz Generator

A Python-based system that extracts Multiple Choice Questions (MCQs)
from question paper images using OCR and NLP, stores them as a
structured dataset, and generates a random quiz.

## Pipeline

Image/PDF → OCR → Preprocessing → ML Classifier → Parser → JSON → Quiz

## Features

- Upload question paper image (JPG/PNG)
- Extract text using EasyOCR
- Classify lines as question / option / noise
- Store MCQs in structured JSON format
- Generate random 10-question quiz with shuffled options
- Score tracking with pass/fail feedback

## Tech Stack

- Python 3.10+
- EasyOCR (OCR engine)
- OpenCV (image processing)
- scikit-learn (TF-IDF + Logistic Regression)
- Pillow, pdf2image

## Project Structure
mcq-extractor/
├── main.py            # Integration pipeline
├── OCR.py             # Text extraction from image
├── preprocessing.py   # Text cleaning and normalization
├── classifier.py      # ML-based line classification
├── mcq_parser.py      # MCQ grouping and JSON storage
├── quiz.py            # Random quiz generator
├── data/
│   └── mcq_bank.json  # Structured MCQ dataset
└── model/             # Saved ML model

## Installation

```bash
pip install easyocr opencv-python pillow scikit-learn joblib pdf2image
```

## Usage

```bash
python main.py
```

Enter the path to your question paper image when prompted.
The system extracts MCQs and launches an interactive quiz.

## Expected Input Format

Works best with clean printed MCQs in this format:

What is RAM?
a) Memory
b) Processor
c) Both
d) None


## Limitations

- OCR accuracy depends on image quality
- Complex multi-column layouts may not parse correctly
- Expects standard a) b) c) d) option format
- No automatic answer detection

## Team

- Member A: OCR + Preprocessing
- Member B: ML Classifier + Parser
- Member C: Quiz Generator + Integration