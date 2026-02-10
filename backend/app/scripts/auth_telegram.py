import asyncio
import os
from telethon import TelegramClient

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
session_name = os.getenv("TELEGRAM_SESSION_NAME", "crypto_sentiment_bot")

if not api_id or not api_hash:
    print("Error: TELEGRAM_API_ID or TELEGRAM_API_HASH not set in environment.")
    print("Please make sure they are set in docker-compose.yml or .env")
    print("\nYou can also enter them now:")
    api_id = input("Enter API ID: ").strip()
    api_hash = input("Enter API Hash: ").strip()

async def auth():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    session_dir = os.path.join(base_dir, "data", "sessions")
    if not os.path.exists(session_dir):
        os.makedirs(session_dir, exist_ok=True)
    
    session_path = os.path.join(session_dir, session_name)
    
    print(f"Starting Telegram authentication for session '{session_name}'...")
    print(f"Data will be stored in: {session_path}.session")
    print("Please follow the prompts to log in.")
    
    client = TelegramClient(session_path, int(api_id), api_hash)
    
    await client.start()
    
    print("\nAuthentication successful!")
    print(f"Session file '{session_name}.session' created.")
    print("You can now restart the backend to start monitoring channels.")
    
    await client.disconnect()

if __name__ == "__main__":
    if not api_id or not api_hash:
        print("Missing credentials.")
        exit(1)
        
    try:
        asyncio.run(auth())
    except KeyboardInterrupt:
        print("\nAuthentication cancelled.")
    except Exception as e:
        print(f"\nError: {e}")
