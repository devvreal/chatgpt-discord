import discord
import os
import openai
import time
import asyncio

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

client = discord.Client(intents=intents)
conversation_histories = {}
last_activity_times = {}

CONVERSATION_RESTART_INTERVAL = 30 * 60

@client.event
async def on_ready():
    print(f"Logged in as {client.user.name}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if client.user.mentioned_in(message):
        user_id = message.author.id

        if user_id in conversation_histories:
            conversation_history = conversation_histories[user_id]
        else:
            conversation_history = []
            conversation_histories[user_id] = conversation_history
        if user_id not in last_activity_times or time.time() - last_activity_times[user_id] > CONVERSATION_RESTART_INTERVAL:
            conversation_history.clear()
            last_activity_times[user_id] = time.time()

        prompt = message.content.replace(client.user.mention, '').strip()
        conversation_history.append(prompt)

        async with message.channel.typing():
            await asyncio.sleep(1)
            response = generate_response(conversation_history)
            if response:
                reply = f"{message.author.mention} {response}"
                await message.channel.send(reply)


def generate_response(conversation):
    API_KEY = os.environ.get('OPENAI_API_KEY')

    if not API_KEY:
        return "OpenAI API key is missing or invalid."

    openai.api_key = API_KEY

    conversation_prompt = "\n".join(conversation[-3:])
    conversation_prompt += "\n"

    retry_count = 0
    while retry_count < 3:
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=conversation_prompt,
                max_tokens=100,
                n=1,
                stop=None,
                temperature=0.9
            )

            if len(response.choices) > 0:
                generated_text = response.choices[0].text.strip()
                if generated_text:
                    return generated_text

            return "Chill, couldn't generate a response."

        except openai.error.RateLimitError:
            print("Rate limit exceede d Retrying after a short delay")
            time.sleep(1)
            retry_count += 1
            continue

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return "An error occurred while generatingresponse"

    return "Chill, couldn't generate a response."

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!memorize'):
        user_id = message.author.id

        if user_id in conversation_histories:
            conversation_history = conversation_histories[user_id]
        else:
            conversation_history = []
            conversation_histories[user_id] = conversation_history

        if user_id not in last_activity_times or time.time() - last_activity_times[user_id] > CONVERSATION_RESTART_INTERVAL:
            conversation_history.clear()
            last_activity_times[user_id] = time.time()

        content = message.content.replace('!memorize', '').strip()
        conversation_history.append(content)

        await message.channel.send("I have memorized that information")

    if client.user.mentioned_in(message):
        user_id = message.author.id

        if user_id in conversation_histories:
            conversation_history = conversation_histories[user_id]
        else:
            conversation_history = []
            conversation_histories[user_id] = conversation_history

        if user_id not in last_activity_times or time.time() - last_activity_times[user_id] > CONVERSATION_RESTART_INTERVAL:
            conversation_history.clear()
            last_activity_times[user_id] = time.time()

        prompt = message.content.replace(client.user.mention, '').strip()
        conversation_history.append(prompt)

        async with message.channel.typing():
            await asyncio.sleep(1)
            response = generate_response(conversation_history)
            if response:

                reply = f"{message.author.mention} {response}"
                await message.channel.send(reply)

client.run(os.environ.get('BOT_TOKEN'))