# PDF Summarizer & Audio Reader (GUI)

A simple **Tkinter** app that:
- Extracts text from a **PDF**
- Creates a concise **summary** (frequency-based extractive method)
- Reads the summary aloud via **gTTS**
- Lets you **save** the summary (.txt) and **export** audio as **.mp3**

> Note: This works best on **text-based PDFs**. Scanned/image-only PDFs won't extract text without OCR.

---

## Features
- Open any PDF and extract text
- Adjustable summary length (1–20 sentences)
- Speak the summary (gTTS) and save as MP3
- Save the summary as .txt
- Clean split-view UI for source text and summary

---

## Tech Stack
- Python 3.8+
- Tkinter
- PyPDF2 (text extraction)
- gTTS (text-to-speech)

---

## Setup
```bash
git clone https://github.com/ramizdevelops/pdf-summarizer.git
cd pdf-summarizer-audio
pip install -r requirements.txt
```

---

## Run
```bash
python app.py
```

---

## Notes
- **gTTS requires internet**.
- If a PDF is scanned, consider adding OCR later (e.g., `pytesseract` + `pdf2image`).

---

## License
MIT — see [LICENSE](LICENSE).