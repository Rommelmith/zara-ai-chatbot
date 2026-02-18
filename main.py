from database import init_db, save_listing, get_all_listings
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from groq import Groq
import re
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse



app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are Zara, the helpful assistant for HandOverIt.com — a Pakistani community platform where people swap and exchange items with others nearby instead of buying or selling.

HOW THE PLATFORM WORKS:
- Users post an item they want to give away or swap
- Other users offer something in exchange
- Both agree on the swap and meet locally
- No money involved — pure exchange

YOUR JOB:
1. Ask the user what item they want to swap
2. Ask about its condition, age, and any important details
3. Ask what they are looking for in return
4. Suggest realistic items they could receive in exchange based on Pakistani market value
5. Help them write a short attractive listing description for their post
6. Encourage them to download the app or post on handoverit.com

TONE:
- Friendly, casual, like a helpful neighbour
- You understand Pakistani market — prices in PKR, local context
- Keep responses to 3-4 sentences
- If user is vague, ask follow up questions before suggesting anything

NEVER:
- Suggest cash transactions — this is a swap only platform
- Suggest unrealistic or very unequal trades
- Give long boring responses
IMPORTANT: When you have collected the item name, condition, and what they want in exchange — end your response with this exact tag:
[LISTING:item=<item>,condition=<condition>,looking_for=<what they want>]
Only add the [LISTING:...] tag when you have CONFIRMED all three details from the user. Never use "unknown" as a value — keep asking until you have real answers.
"""


@app.on_event("startup")
async def startup():
    init_db()
    print("Database initialized")


@app.get("/", response_class=HTMLResponse)
def home():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("messages", [])

    def generate():
        full_response = ""

        stream = client.chat.completions.create(
            model = MODEL,
            stream=True,
            messages = [
                {"role":"system", "content":SYSTEM_PROMPT},
                *message,
            ]
        )

        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text is None:
                continue
            full_response += text
            yield text
        match = re.search(
            r'\[LISTING:item=([^,\]]+),condition=([^,\]]+),looking_for=([^\]]+)\]',
            full_response
        )
        if match:
            item = match.group(1).strip()
            condition = match.group(2).strip()
            looking_for = match.group(3).strip()

            if item != "unknown" and looking_for != "unknown":
                save_listing(item, condition, looking_for)

    return StreamingResponse(generate(), media_type="text/plain")


@app.get("/listings")
def listings():
    data = get_all_listings()
    return JSONResponse(content={"listings": data})

