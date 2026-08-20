import os
import threading
import discord
from flask import Flask
from google import genai
from google.genai import types

# ==========================================
# 1. FLASK SERVER (Render Keep-Alive)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Quix Bot is online!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# ==========================================
# 2. GEMINI AI CONFIGURATION (No Search Grounding)
# ==========================================
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Load instructions and custom knowledge files
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


# ==========================================
# 3. DISCORD BOT SETUP
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        # Ignore messages sent by the bot itself
        if message.author == self.user:
            return

        # Trigger when mentioned or in direct messages
        if self.user in message.mentions or isinstance(message.channel, discord.DMChannel):
            user_message = message.content.replace(f'<@!{self.user.id}>', '').replace(f'<@{self.user.id}>', '').strip()
            
            if not user_message:
                await message.reply("Hey! What do you want to talk about?")
                return

            async with message.channel.typing():
                try:
                    response = await client.aio.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=user_message,
                        config=types.GenerateContentConfig(
                            system_instruction=bot_system_prompt,
                            temperature=0.7
                        )
                    )
                    
                    reply = response.text if response.text else "Received an empty response."

                    # Handle Discord 2000 character limit
                    if len(reply) > 2000:
                        for i in range(0, len(reply), 1900):
                            await message.channel.send(reply[i:i+1900])
                    else:
                        await message.reply(reply)

                except Exception as e:
                    print(f"Error details: {e}")
                    await message.reply("Oops, had trouble processing that request. Try again in a moment!")


# ==========================================
# 4. START SERVICES
# ==========================================
if __name__ == '__main__':
    # Start web server thread
    threading.Thread(target=run_web, daemon=True).start()

    # Start Discord Bot
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if not TOKEN:
        raise ValueError("DISCORD_TOKEN environment variable is missing!")

    client_bot = MyClient(intents=intents)
    client_bot.run(TOKEN)