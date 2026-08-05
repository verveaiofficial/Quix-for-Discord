import os
import discord
from google import genai
from google.genai import types

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Initialize Gemini client
ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Set your AI's personality or rules here
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
                model="gemini-2.5-flash",
                contents=message.content,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                ),
            )
            await message.reply(response.text)
        except Exception as e:
            await message.reply("My brain hiccuped. Try again in a second!")

client.run(os.getenv("DISCORD_TOKEN"))
