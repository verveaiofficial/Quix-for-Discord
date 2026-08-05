import os
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
