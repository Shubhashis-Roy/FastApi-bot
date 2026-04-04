import strawberry
from typing import List
from .db import messages_collection
from .claude import ask_claude
from datetime import datetime
import json

@strawberry.type
class Message:
    id: strawberry.ID
    user: str
    bot: str
    timestamp: str

def sanitize_bot_response(bot: str) -> str:
    if not bot:
        return bot

    if "Claude error" in bot or "invalid_request_error" in bot:
        if "credit balance is too low" in bot:
            return "AI service quota exceeded. Please try again later."
        return "AI service is temporarily unavailable."

    return bot

@strawberry.type
class Query:
    @strawberry.field
    async def chat_history(self) -> List[Message]:
        cursor = messages_collection.find().sort("timestamp", -1).limit(10)

        messages = []
        async for doc in cursor:
            messages.append(
                Message(
                    id=str(doc["_id"]),   
                    user=doc["user"],
                    # bot=doc["bot"],
                    bot=sanitize_bot_response(doc.get("bot", "")),
                    timestamp=doc["timestamp"],
                )
            )

        return messages

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def send_message(self, text: str, products: str) -> Message:
        try:
            products = json.loads(products)  # ✅ FIX

            context = ""

            for p in products:
                title = p.get("title", "")
                desc = p.get("description", "")
                variants = p.get("variants", {}).get("nodes", [])
                price = variants[0].get("price") if variants else ""

                context += f"Title: {title}\nDescription: {desc}\nPrice: {price}\n\n"

            prompt = f"""
                    You are a Shopify store assistant.

                    Products:
                    {context}

                    User question:
                    {text}

                    Answer ONLY using the provided products.
                    If no relevant product, say "No matching products found".
                    """

            reply = await ask_claude(prompt)

        except Exception as e:
            print("Error:", str(e))
            reply = getattr(e, "message", "Something went wrong.")

        message = {
            "user": text,
            "bot": reply,
            "timestamp": datetime.utcnow().isoformat()
        }

        result = await messages_collection.insert_one(message)

        return Message(
            id=str(result.inserted_id),
            user=message["user"],
            bot=message["bot"],
            timestamp=message["timestamp"],
        )
schema = strawberry.Schema(query=Query, mutation=Mutation)