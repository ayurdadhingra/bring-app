# Kassenbon-Einkaufslisten-Abgleich

Automatisierung der Einkaufslistenverwaltung durch KI-gestützte Beleglesung
- Dokumentenverarbeitung: OCR-basierte Textextraktion aus Kassenbon-Fotos mittels PyTesseract
- Zuordnung von Produktkategorien: Qwen3 mit Outlines-Decoding für strukturierte Outputs
- API-Anbindung: Verwendet offizielle Bring Einkaufslisten-App API zur Entfernung erworbener Artikel


## Setup

Setup environment:

```bash
uv sync
```

Pull LLM with ollama:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral
```

Run basic demo:

```bash
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
python receipt_parsing_pytesseract.py
```