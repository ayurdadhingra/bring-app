# Kassenbon–Einkaufslisten–Abgleich (DeepseekOCR Version)

Dieses Projekt automatisiert den Abgleich zwischen einem fotografierten Kassenbon und einer Einkaufsliste in der Bring! App.
Es kombiniert moderne OCR-Techniken, LLM-basierte Produktklassifizierung und asynchrone API-Anfragen.

## Features
1. Dokumentenverarbeitung

Extraktion von Text und Produktlinien aus Kassenbon-Fotos

Verwendet DeepseekOCR für robuste OCR-Erkennung

2. Produktkategorisierung

Vergleicht die gescannten Kassenbon-Artikel mit den Artikeln auf der Einkaufsliste und hakt die entsprechenden Artikel dort ab.

Modell: Qwen / Qwen2.5-7B-Instruct

Decoding-Methode: Outlines decoding für zuverlässige, strukturierte JSON-Ausgaben

3. API-Anbindung

Automatisierte Entfernung gekaufter Artikel aus der Bring! Einkaufslisten-App

Nutzung der offiziellen Bring-API

Vollständig asynchron implementiert mit asyncio und aiohttp

## Setup (Kaggle Notebook)

Öffne das Notebook in deiner Kaggle-Umgebung.

Lade die Datei bring_client_kaggle.py hoch:

Als eigenes Dataset

Benenne das Dataset: bring-client

Lade dein Kassenbon-Bild (z. B. receipt.jpg) ebenfalls als Dataset hoch.

Importiere beide Datasets in das Notebook.

Das Skript ist nun vollständig ausführbar.