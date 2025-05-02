import os
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))

async def suggest_title(text: str) -> str:
    prompt = f"Suggest a concise title for a to-do task based on: {text}"
    response = await asyncio.to_thread(model.generate_content, prompt)
    return response.text.strip()

async def suggest_description(text: str) -> str:
    prompt = f"Write a detailed description for a task titled: '{text}'"
    response = await asyncio.to_thread(model.generate_content, prompt)
    return response.text.strip()

async def summarize_text(text: str) -> str:
    prompt = f"Summarize this task description: {text}"
    response = await asyncio.to_thread(model.generate_content, prompt)
    return response.text.strip()
