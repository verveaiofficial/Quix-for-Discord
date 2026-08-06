import os
import threading
import discord
from discord.ext import commands
from flask import Flask
import google.generativeai as genai

# ==========================================
# 1. FLASK SERVER (Render Keep-Alive)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Quix Luna is online and searching the web!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


# ==========================================
# 2. GEMINI AI CONFIGURATION (With Search)
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Initializing Gemini model with Google Search grounding enabled
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    tools="google_search"
)


# ==========================================
# 3. DISCORD BOT SETUP
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("Quix Luna is active with live Web Search enabled!")

@bot.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    # Trigger when mentioned or in direct messages
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            try:
                # Remove bot tag from prompt
                user_prompt = message.content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()

                if not user_prompt:
                    await message.channel.send("Hey! What do you want to talk about or search for?")
                    return

                # Get response from Gemini (will automatically search Google if needed)
                response = model.generate_content(user_prompt)
                reply = response.text

                # Handle Discord 2000 character limit
                if len(reply) > 2000:
                    for i in range(0, len(reply), 1900):
                        await message.channel.send(reply[i:i+1900])
                else:
                    await message.channel.send(reply)

            except Exception as e:
                print(f"Error processing message: {e}")
                await message.channel.send("Oops, had trouble processing that request. Try again in a moment!")

    await bot.process_commands(message)


# ==========================================
# 4. START SERVICES
# ==========================================
if __name__ == "__main__":
    # Start Flask keep-alive thread
    threading.Thread(target=run_flask, daemon=True).start()

    # Start Discord Bot
    DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN environment variable is missing!")

    bot.run(DISCORD_TOKEN) os
import threading
import discord
from flask import Flask
from google import genai
from google.genai import types

app = Flask(__name__)

@app.route('/')
def home():
    return "Quix Bot is online!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
TOKEN = os.environ.get("DISCORD_TOKEN")

try:
    with open("instructions.txt", "r", encoding="utf-8") as f:
        instructions = f.read()
except FileNotFoundError:
    instructions = "You are a helpful assistant."

try:
    with open("knowledge.txt", "r", encoding="utf-8") as f:
        knowledge = f.read()
except FileNotFoundError:
    knowledge = ""

bot_system_prompt = f"{instructions}\n\nCustom Knowledge Base:\n{knowledge}"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if self.user in message.mentions:
            user_message = message.content.replace(f'<@!{self.user.id}>', '').replace(f'<@{self.user.id}>', '').strip()
            
            try:
                # Async call keeps the bot responsive and fast
                response = await client.aio.models.generate_content(
                    model='gemini-3.1-flash-lite',
                    contents=user_message,
                    config=types.GenerateContentConfig(
                        system_instruction=bot_system_prompt,
                        temperature=0.7
                    )
                )
                if response.text:
                    await message.reply(response.text)
                else:
                    await message.reply("Received an empty response.")
            except Exception as e:
                print(f"Error details: {e}")
                await message.reply(f"Error: {e}")

client_bot = MyClient(intents=intents)

if __name__ == '__main__':
    client_bot.run(TOKEN)