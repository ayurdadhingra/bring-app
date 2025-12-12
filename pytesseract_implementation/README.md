# Kassenbon-Einkaufslisten-Abgleich

- Dokumentenverarbeitung: OCR-basierte Textextraktion aus Kassenbon-Fotos

  - CPU-Version: PyTesseract

  - Kaggle/GPU: DeepSeekOCR

- Zuordnung von Produktkategorien:

  - CPU-Version: Llama 3.2 3B

  - Kaggle/GPU: Qwen/Qwen2.5-7B-Instruct mit Outlines-Decoding für strukturierte Outputs

- API-Anbindung: Verwendet offizielle Bring Einkaufslisten-App API zur Entfernung erworbener Artikel unter Nutzung von asyncio/aiohttp für asynchrone API-Anfragen

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
