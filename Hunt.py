import discord, json
from discord.ext import commands
from discord.utils import get


TOKEN = ""
BOT_NAME = ""
channels = {}

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix = '!', intents=intents)

# load config
def load():

    global TOKEN, BOT_NAME, channels

    with open("config.json") as json_file:
        config = json.load(json_file)

        TOKEN = config["TOKEN"]
        BOT_NAME = config["BOT_NAME"]
        channels = config["channels"]


# save config
def save():

    global TOKEN, BOT_NAME, channels

    with open("config.json", "w") as json_file:
        json.dump({"TOKEN": TOKEN, "BOT_NAME": BOT_NAME, "channels": channels}, json_file)


######################### BOT EVENTS


# respond to new messages
@bot.event
async def on_message(message):

    global channels, BOT_NAME

    if str(message.author) == BOT_NAME:
        return

    # a PM is received
    if not message.guild:

        passwords = [i["password"] for i in channels]

        if message.content.strip() not in passwords:
            await message.channel.send("Wrong password.")
            return

        for channel in channels:
            target = get(bot.get_all_channels(), name=channel["name"])

            if message.author in target.members:
                continue

            if message.content.strip() == channel["password"]:
                if channel["claimed"] == channel["limit"]:
                    await message.channel.send("I'm afraid you are too late.")
                    continue

                target = get(bot.get_all_channels(), name=channel["name"])
                await target.set_permissions(message.author, read_messages=True, send_messages=True)

                channel["claimed"] += 1
                save()

                await message.channel.send("You've been added to: " + channel["name"])

                if channel["claimed"] == channel["limit"]:
                    await target.send("This channel is now full.")
    
    await bot.process_commands(message)


# bot is online
@bot.event
async def on_ready():

    print("ONLINE")


# ERROR HANDLER
@bot.event
async def on_command_error(ctx, error):

    await ctx.send("Error: " + str(error))


######################### BOT COMMANDS


# join voice channel of caller
@bot.command(description="Add another channel", aliases=["Add", "ADD"])
async def add(ctx, name, limit, password):

    global channels

    channel = get(ctx.guild.channels, name=name)

    if not channel:
        await ctx.channel.send("Channel doesn't exist")
        return
    
    for ch in channels:
        if ch["name"] == name:
            await ctx.channel.send("Channel is already added.")
            return

    channels.append({"name": name, "limit": int(limit), "claimed": 0, "password": password})
    save()
    
    await ctx.channel.send("Success")


# reset channels
@bot.command(description="Remove all channels from data", aliases=["Reset", "RESET"])
async def reset(ctx):

    global channels

    channels = []
    save()

    await ctx.channel.send("Success")


load()
bot.run(TOKEN, bot=True)
