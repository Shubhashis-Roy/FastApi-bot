import strawberry
from typing import List
from db import messages_collection
from claude import ask_claude
from datetime import datetime

@strawberry.type
class Message:
    id: strawberry.ID
    user: str
    bot: str
    timestamp: str


@strawberry.type
class Query:
    @strawberry.field
    async def chat_history(self) -> List[Message]:
        cursor = messages_collection.find().sort("timestamp", -1).limit(10)

        messages = []
        async for doc in cursor:
            messages.append(
                Message(
                    id=str(doc["_id"]),   # ✅ map Mongo _id → GraphQL id
                    user=doc["user"],
                    bot=doc["bot"],
                    timestamp=doc["timestamp"],
                )
            )

        return messages


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def send_message(self, text: str) -> Message:
        reply = await ask_claude(text)

        message = {
            "user": text,
            "bot": reply,
            "timestamp": datetime.utcnow().isoformat()
        }

        result = await messages_collection.insert_one(message)

        return Message(
            id=str(result.inserted_id),  # ✅ REQUIRED
            user=message["user"],
            bot=message["bot"],
            timestamp=message["timestamp"],
        )


schema = strawberry.Schema(query=Query, mutation=Mutation)