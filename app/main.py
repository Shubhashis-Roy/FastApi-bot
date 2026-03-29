from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from .schema import schema
from dotenv import load_dotenv
from .db import ping_db
import os
import uvicorn
from fastapi.responses import Response, HTMLResponse


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await ping_db()
    print("MongoDB is connected successfully!")


graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/widget.js")
def widget():
    js_code = """
    (function () {
        const iframe = document.createElement('iframe');
        iframe.src = 'https://shopify-app-95ky.onrender.com/chatbot';
        iframe.style.position = 'fixed';
        iframe.style.bottom = '20px';
        iframe.style.right = '20px';
        iframe.style.width = '350px';
        iframe.style.height = '500px';
        iframe.style.border = 'none';
        iframe.style.zIndex = '9999';

        document.body.appendChild(iframe);
    })();
    """
    return Response(content=js_code, media_type="application/javascript")


@app.get("/chatbot")
def chatbot():
    return HTMLResponse("""
        <html>
            <body>
                <h3>Chatbot Loaded</h3>
                <div id="chatbot-ui">Your chatbot UI here</div>
            </body>
        </html>
    """)

# ---- Entry Point ----
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True,   
    )