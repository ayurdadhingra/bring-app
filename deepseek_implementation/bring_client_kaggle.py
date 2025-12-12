import asyncio
import aiohttp
import logging
import os
from typing import List, Dict, Any
from python_bring_api.bring import Bring
from kaggle_secrets import UserSecretsClient
import nest_asyncio
nest_asyncio.apply()
# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
user_secrets = UserSecretsClient()
# Load credentials from environment variables
EMAIL = user_secrets.get_secret("BRING_API_EMAIL")
KEY = user_secrets.get_secret("BRING_API_KEY")

if not EMAIL or not KEY:
    raise ValueError("Please set BRING_API_EMAIL and BRING_API_KEY in environment variables.")

# -------------------- ASYNC HELPERS -------------------- #

async def login_bring(session: aiohttp.ClientSession) -> Bring:
    """
    Create and login Bring instance asynchronously.
    """
    bring = Bring(EMAIL, KEY, sessionAsync=session)
    await bring.loginAsync()
    logging.info(f"✅ Logged in to Bring! as {EMAIL}")
    return bring

async def load_lists(bring: Bring) -> List[Dict[str, Any]]:
    """
    Fetch all available shopping lists for the logged-in user.
    """
    lists = (await bring.loadListsAsync()).get("lists", [])
    logging.info(f"Loaded {len(lists)} shopping list(s).")
    return lists

async def load_items(bring: Bring, list_uuid: str) -> Dict[str, Any]:
    """
    Get all items from a specific shopping list.
    """
    items = await bring.getItemsAsync(list_uuid)
    logging.info(f"Loaded {len(items)} items from list {list_uuid}.")
    return items

async def save_item(bring: Bring, list_uuid: str, name: str, note: str = ""):
    """
    Save an item with optional specifications to a shopping list.
    """
    await bring.saveItemAsync(list_uuid, name, note)
    logging.info(f"Saved item '{name}' to list {list_uuid}.")

async def check_off_item(bring: Bring, list_uuid: str, name: str):
    """
    Mark an item as completed (checked off) in a list.
    """
    await bring.completeItemAsync(list_uuid, name)
    logging.info(f"Checked off item '{name}' in list {list_uuid}.")

async def remove_item(bring: Bring, list_uuid: str, name: str):
    """
    Remove an item from a list.
    """
    await bring.removeItemAsync(list_uuid, name)
    logging.info(f"Removed item '{name}' from list {list_uuid}.")

