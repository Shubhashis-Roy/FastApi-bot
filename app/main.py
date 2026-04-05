from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from .schema import schema
from dotenv import load_dotenv
from .db import ping_db
import os
import uvicorn

load_dotenv()

app = FastAPI()

# ✅ CORS (keep as-is)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 🔥 CRITICAL: Allow Shopify iframe embedding
@app.middleware("http")
async def allow_shopify_iframe(request: Request, call_next):
    response: Response = await call_next(request)

    # Allow embedding in Shopify admin + storefront
    response.headers["Content-Security-Policy"] = (
        "frame-ancestors https://*.myshopify.com https://admin.shopify.com;"
    )

    # Remove blocking header if present
    if "x-frame-options" in response.headers:
        del response.headers["x-frame-options"]

    return response


# ✅ Startup
@app.on_event("startup")
async def startup():
    await ping_db()
    print("MongoDB is connected successfully!")


# ✅ GraphQL
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


# ---- Entry Point ----
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True,
    )