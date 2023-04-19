import discord
import responses

async def send_message(message:str, user_message:str, guild_id:int, is_private:bool, is_command:bool):
    response = await responses.handle_responses(message, user_message, guild_id, is_command)
    if type(response) == str:
        await message.author.send(response) if is_private else await message.channel.send(response)
    elif type(response) == discord.Embed:
        await message.channel.send(embed=response)

def run_discord_bot():
    TOKEN = "" #<-- your token here
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f'{client.user} is running')

    @client.event
    async def on_message(message:discord.MessageType):
        if message.author == client.user:
            return
        
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        guild_id = message.guild.id

        print(f"{username} said: '{user_message}'({guild_id}/{channel})")

        if user_message[0] == '!':
            user_message = user_message[1:]
            await send_message(message, user_message, guild_id, is_private=True, is_command=True)
        else:
            await send_message(message, user_message, guild_id, is_private=False, is_command=False)
    client.run(TOKEN)

