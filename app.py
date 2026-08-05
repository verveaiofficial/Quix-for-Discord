import os
import discord
from google import genai
from google.genai import types

# Initialize clients
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
TOKEN = os.environ.get("DISCORD_TOKEN")

# Read instructions file safely
try:
    with open("instructions.txt", "r", encoding="utf-8") as f:
        instructions = f.read()
except FileNotFoundError:
    instructions = "You are a helpful assistant."

# Read knowledge file safely
try:
    with open("knowledge.txt", "r", encoding="utf-8") as f:
        knowledge = f.read()
except FileNotFoundError:
    knowledge = ""

# Combine them into a single system instruction
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
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=user_message,
                    config=types.GenerateContentConfig(
                        system_instruction=bot_system_prompt,
                        temperature=0.7
                    )
                )
                await message.reply(response.text)
            except Exception as e:
                await message.reply("Oops, something went wrong processing that!")

client_bot = MyClient(intents=intents)

if __name__ == '__main__':
    client_bot.run(TOKEN)