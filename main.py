import os
import pandas as pd
import requests
import httpx
import json
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
def serve_login():
    return FileResponse("login.html")

@app.post("/login")
async def login(request: Request, response: Response):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    valid_users = ["ritik", "anjali", "sundram"]
    valid_password = "Sundar@123"
    if username in valid_users and password == valid_password:
        response.set_cookie(key="username", value=username)
        return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/profile")
def profile(request: Request):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse("/")
    return JSONResponse({"username": username, "message": f"Welcome, {username}!"})

@app.get("/logout")
def logout(response: Response):
    response.delete_cookie(key="username")
    return RedirectResponse("/")

@app.get("/dashboard")
def serve_dashboard():
    return FileResponse("dashboard.html")

OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

@app.post("/ai-chat")
async def ai_chat(request: Request):
    data = await request.json()
    user_message = data.get("message")
    if user_message:
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": user_message}
                ]
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(OPENROUTER_API_URL, headers=headers, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    answer = result["choices"][0]["message"]["content"]
                else:
                    answer = f"Error: {response.text}"
        except Exception as e:
            answer = f"Error: {str(e)}"
    else:
        answer = "Please ask a question."
    return {"answer": answer}

@app.post("/save-chat")
async def save_chat(request: Request):
    data = await request.json()
    session_title = data.get("title", "New chat")
    messages = data.get("messages", [])
    with open("chat_history.txt", "a", encoding="utf-8") as f:
        f.write(f"Session: {session_title}\n")
        for msg in messages:
            f.write(f"{msg['role']}: {msg['content']}\n")
        f.write("-"*40 + "\n")
    return {"status": "saved"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)

