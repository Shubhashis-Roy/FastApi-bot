from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()  # <-- MUST be here

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI is not set")

client = AsyncIOMotorClient(MONGODB_URI)
db = client.chatbot
messages_collection = db.messages

async def ping_db():
    await client.admin.command("ping")