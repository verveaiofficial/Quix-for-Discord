import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Load instructions
try:
    with open("instructions.txt", "r", encoding="utf-8") as f:
        instructions = f.read()
except FileNotFoundError:
    instructions = "You are a helpful assistant."

# Load knowledge
try:
    with open("knowledge.txt", "r", encoding="utf-8") as f:
        knowledge = f.read()
except FileNotFoundError:
    knowledge = ""

# Combine them into a single system instruction
bot_system_prompt = f"{instructions}\n\nCustom Knowledge Base:\n{knowledge}"

# Inside your message handling function when calling Gemini:
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=user_message,
    config=types.GenerateContentConfig(
        system_instruction=bot_system_prompt,
        temperature=0.7
    )
) os
import threading
from flask import Flask
import discord
from google import genai
from google.genai import types

# Tiny web server to keep Render happy
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is active!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Discord Bot setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = "You are a helpful, witty AI assistant..."

@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    async with message.channel.typing():
        try:
            response = ai_client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=message.content,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                ),
            )
            await message.reply(response.text)
        except Exception as e:
            await message.reply("My brain hiccuped. Try again in a second!")

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    client.run(os.getenv("DISCORD_TOKEN"))
