import logging
import sys
import os
import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv
from python_bring_api.bring import Bring
import aiohttp
# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='[%(levelname)s] %(message)s')


# -------------------- AUTHENTICATION -------------------- #

def login_bring() -> Bring:
    """
    Log in to the Bring! API.
    - First tries to use credentials from .env (BRING_API_EMAIL and BRING_API_KEY).
    - If not found, prompts the user interactively.
    """
    email = os.getenv("BRING_API_EMAIL")
    key = os.getenv("BRING_API_KEY")

    if not email or not key:
        print("\n--- Bring! credentials not found in .env ---")
        print("Please enter your credentials:")
        email = input("Email: ").strip()
        key = input("Password/API Key: ").strip()

    bring = Bring(email, key)
    async def _do_login():
        bring._session = aiohttp.ClientSession()
        await bring.loginAsync()
        return bring

    try:
        loop = asyncio.get_running_loop()
        # Already in an event loop (e.g., Kaggle)
        logging.info("Detected running event loop — using create_task() for async login.")
        task = loop.create_task(_do_login())
        bring_instance = loop.run_until_complete(task)
    except RuntimeError:
        # No running event loop (normal Python)
        bring_instance = asyncio.run(_do_login())
    
    logging.info(f"Successfully logged in to Bring! as {email}")
    return bring


# -------------------- SHOPPING LIST MANAGEMENT -------------------- #

def load_lists(bring: Bring) -> List[Dict[str, Any]]:
    """
    Fetch all available shopping lists for the logged-in user.
    """
    lists = bring.loadLists().get("lists", [])
    logging.info(f"Loaded {len(lists)} shopping list(s).")
    return lists


def load_items(bring: Bring, lists: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get all the items for the first shopping list in the Bring account.
    """
    if not lists:
        raise ValueError("No shopping lists available to load items from.")

    list_uuid = lists[0]['listUuid']
    items = bring.getItems(list_uuid)
    logging.info(f"Loaded items from list '{lists[0].get('name', list_uuid)}'")
    return items


def check_off_item(bring: Bring, lists: List[Dict[str, Any]], item_name: str) -> None:
    """
    Mark an item as completed (checked off) in the first shopping list.
    """
    if not lists:
        raise ValueError("No shopping lists available to check off items.")

    list_uuid = lists[0]['listUuid']
    bring.completeItem(list_uuid, item_name)
    logging.info(f"Checked off item: {item_name}")


def remove_item(bring: Bring, lists: List[Dict[str, Any]], item_name: str) -> None:
    """
    Remove an item from the first shopping list.
    """
    if not lists:
        raise ValueError("No shopping lists available to remove items from.")

    list_uuid = lists[0]['listUuid']
    bring.removeItem(list_uuid, item_name)
    logging.info(f"Removed item: {item_name}")


# -------------------- MAIN TEST -------------------- #

if __name__ == "__main__":
    try:
        bring_instance = login_bring()
        lists = load_lists(bring_instance)
        items = load_items(bring_instance, lists)
        logging.info(f"Current items: {items}")

        # Example action
        check_off_item(bring_instance, lists, 'Kiwis')

    except Exception as e:
        logging.error(f"Error: {e}")
