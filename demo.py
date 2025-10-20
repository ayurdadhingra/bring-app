import re
import cv2
import pytesseract
import shutil
import json
import requests
from typing import List, Dict, Tuple, Optional
from bring_client import login_bring, load_lists, load_items, check_off_item
import os
from dotenv import load_dotenv

load_dotenv()


# -------------------- OCR MODULE -------------------- #

def extract_text_from_image(image_path: str) -> List[str]:
    """
    Extract text from a receipt image using OCR.
    Returns a list of detected text lines.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image at path: {image_path}")

    # Preprocess image for OCR
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    blurred = cv2.GaussianBlur(thresh, (5, 5), 0)
    resized = cv2.resize(blurred, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

    # OCR
    pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")
    text = pytesseract.image_to_string(resized, lang="deu")
    return [line.strip() for line in text.splitlines() if line.strip()]


# -------------------- LLM MATCHING MODULE -------------------- #

def ollama_infer(receipt_item: str, bring_items_list: List[str]) -> str:
    """
    Query local LLM (Ollama) to match a receipt item with Bring list items.
    Returns the best match or 'No match found'.
    """
    url = "http://127.0.0.1:11434/api/generate"
    prompt = (
        "You are a receipt parsing assistant.\n"
        "Your task is to check whether a given item appears in a predefined list of items (Item_list).\n"
        "If the item is not a grocery item (e.g., fruits, vegetables, household items) skip it.\n"
        "- Item names may be in a different language.\n"
        "- The item list might contain brand names instead of product names.\n"
        "- Items might appear as partial matches in the receipt.\n"
        f"Item_list: {bring_items_list}\n"
        f"Item: {receipt_item}\n"
        "Return either the exact matching item from the list or 'No match found'."
    )

    ollama_api_token = os.getenv("OLLAMA_API_TOKEN")
    if not ollama_api_token:
        raise ValueError("Please ensure OLLAMA_API_TOKEN environment variable is set.")

    headers = {
        "Authorization": OLLAMA_API_TOKEN
    }

    try:
        response = requests.post(url, json={"model": "mistral", "prompt": prompt},
                                 headers=headers, stream=True)
        collected = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                collected += data.get("response", "")
        return collected.strip() if collected else "No match found"

    except Exception as e:
        print(f"Error during Ollama inference for item '{receipt_item}': {e}")
        return "No match found"


# -------------------- CATEGORIZATION MODULE -------------------- #

def categorize_items(receipt_items: List[str], bring_items: List[str]) -> Dict[str, str]:
    """
    Match receipt text lines to items in the Bring shopping list.
    Returns a dict {receipt_item: matched_bring_item}.
    """
    categorized = {}

    for item in receipt_items:
        # Filter out prices or short strings
        if len(item) < 2 or re.match(r'^\$?\d+([.,]\d{1,2})?$', item):
            continue

        print(f"Processing receipt item: {item} ...")
        match = ollama_infer(item, bring_items)
        if match and match != "No match found":
            categorized[item] = match

    return categorized


# -------------------- BRING API MODULE -------------------- #

def bring_login_and_fetch() -> Optional[Tuple[object, dict]]:
    """
    Log into Bring! and fetch available shopping lists.
    """
    bring_instance = login_bring()
    all_lists = load_lists(bring_instance)
    if not all_lists:
        print("No shopping lists found.")
        return None
    return bring_instance, all_lists


def fetch_bring_items(bring_instance, all_lists) -> List[str]:
    """
    Extract item names from Bring 'purchase' list.
    """
    current_items = load_items(bring_instance, all_lists)
    return [item['name'] for item in current_items.get('purchase', [])]


def update_bring_list(bring_instance, all_lists, categorized_items: Dict[str, str]) -> None:
    """
    Check off items in Bring! based on categorized receipt matches.
    """
    if not categorized_items:
        print("No matching items found on the receipt for your Bring! list.")
        return

    for receipt_item, bring_item in categorized_items.items():
        print(f"- Receipt: '{receipt_item}' → Bring: '{bring_item}'")
        check_off_item(bring_instance, all_lists, bring_item)


# -------------------- ORCHESTRATION -------------------- #

def process_receipt(image_path: str, bring_items: List[str]) -> Dict[str, str]:
    """
    Full pipeline for processing a single receipt:
    - Extract OCR text
    - Categorize against Bring items
    """
    print(f"Processing receipt: {image_path}")
    extracted_items = extract_text_from_image(image_path)
    categorized = categorize_items(extracted_items, bring_items)

    print("\nCategorized Items:")
    for item, category in categorized.items():
        print(f"- {item}: {category}")

    return categorized


# -------------------- MAIN ENTRY POINT -------------------- #

if __name__ == "__main__":
    bring_data = bring_login_and_fetch()
    if bring_data:
        bring_instance, all_lists = bring_data
        bring_items = fetch_bring_items(bring_instance, all_lists)
        categorized = process_receipt("receipt.jpg", bring_items)
        update_bring_list(bring_instance, all_lists, categorized)
