# Conversational Games Bot for Discord.
# Last updated 13-01-2021

## Imports.
# Discord (API Wrapper)
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

# Asynchronous Requests
import aiohttp
import asyncio
import keep_alive
import os

# Date/Time
from datetime import datetime

# Randomization
from random import choice

# Parsing
import json
import html

## Constants.
# Load the config.json into a 'CONFIG' variable.
with open('config.json') as f:
	CONFIG = json.load(f)

CLIENT_SESSION = aiohttp.ClientSession()
COLOR_RED = 0xEF2928
COLOR_BLUE = 0x0094E6

## Info.
print("=" * 25)
print("Conversational Games Bot")
print("=" * 25)
print("1.0.0 | Release | By Anomic", '\n')

## Functions.
def parse_list_file(file_path: str) -> list:
	"""Parse a text file into a list containing each line."""
	
	with open(file_path) as f:
		return [l.strip() for l in f.readlines() if l.strip()]

get_invite = lambda bot_id: f"https://discord.com/api/oauth2/authorize?client_id={bot_id}&permissions=280640&scope=bot"

## Responses.
print("[Loading] Loading responses...")
# Open all the text files and load them into list variables in a dictionary.
database = {
	"truths": parse_list_file('data/truths.txt'),
	"dares": parse_list_file('data/dares.txt'),
	"nhie": parse_list_file('data/nhie.txt'),
	"tot": parse_list_file('data/tot.txt')
}

## Setup.
print("[Set-Up] Setting up bot..")
client = commands.Bot(
	command_prefix = CONFIG['BOT_PREFIX'],
	case_insensitive = True,
	intents = discord.Intents(messages=True, guilds=True, reactions=True)	
)
client.remove_command('help')

## Events.
@client.event
async def on_connect():
	""""https://discordpy.readthedocs.io/en/latest/api.html#discord.on_connect"""
	
	print("[Connected] Established connection with Discord.")

@client.event
async def on_ready():
	"""https://discordpy.readthedocs.io/en/latest/api.html#discord.on_ready"""
	
	print(f"[Ready] Bot is ready. Logged in as {client.user}.", '\n')
	await client.change_presence(activity=discord.Activity(name=choice(CONFIG['PLAYING_STATUSES']), type=discord.ActivityType.playing))

@client.event
async def on_disconnect():
	"""https://discordpy.readthedocs.io/en/latest/api.html#discord.on_disconnect"""

	print("[Disconnected] Lost connection with Discord.")

@client.event
async def on_guild_join(guild):
	"""https://discordpy.readthedocs.io/en/latest/api.html#discord.on_guild_join"""

	print(f"[Guild] Added to: {guild.name} (id: {guild.id}). This guild has {guild.member_count} members!")

@client.event
async def on_guild_remove(guild):
	"""https://discordpy.readthedocs.io/en/latest/api.html#discord.on_guild_remove"""

	print(f"[Guild] Removed from: {guild.name} (id: {guild.id}).")

@client.event
async def on_command_error(ctx, error):
	"""https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.on_command_error"""

	error = getattr(error, 'original', error)
	ignored = (commands.CommandNotFound, commands.MissingPermissions)

	if isinstance(error, ignored):
		return
	elif isinstance(error, commands.CommandOnCooldown):
		return await ctx.send(f"\⛔ **This command is on cooldown. Try again in {error.retry_after:.2f}s.**", delete_after = 7)
	else:
		return print(f"[Exception] An exception has occured. {error}")

## Commands.
@client.command(aliases = ['commands', 'help'])
@commands.cooldown(1, 5, BucketType.channel)
async def cmds(ctx):
	"""General info about the bot and command help."""

	embed = discord.Embed(title = "Conversational Games Bot", url = "https://github.com/waterrmalann/discord-conversational-games-bot")
	embed.add_field(
		name = "» About",
		value = "Hello! I'm a Conversational Games Bot. " \
			"I have a huge database of questions for text based games such as " \
			"Truth or Dare, Never Have I Ever, Would You Rather, etc... " \
			"I can help keep your chat active and fun :)",
		inline = False
	)
	embed.add_field(
		name = "» Games",
		value = f"• Truth or Dare (`{CONFIG['BOT_PREFIX']}(t)ruth`, `{CONFIG['BOT_PREFIX']}(d)are`)\n" \
			f"• Never Have I Ever (`{CONFIG['BOT_PREFIX']}(n)ever`)\n" \
			f"• Would You Rather (`{CONFIG['BOT_PREFIX']}wyr`)\n" \
			f"• This Or That (`{CONFIG['BOT_PREFIX']}tot`)\n" \
			f"• Will You Press The Button (`{CONFIG['BOT_PREFIX']}wyp`)",
		inline = False
	)
	embed.add_field(
		name = "» Links",
		value = f"\🔗 **[Invite me to your server!]({get_invite(client.user.id)})**\n" \
			f"\🔗 **[Support / Suggestions / Feedback]({CONFIG['SUPPORT_SERVER']})**",
		inline = False
	)
	embed.set_footer(text = "Made with ❤️ by WaterrMalann#1700")
	await ctx.send(embed = embed)

@client.command(aliases = ['t'])
@commands.cooldown(1, 2.5, BucketType.user)
async def truth(ctx):
	"""Get a truth question."""
	
	response = f"**Truth:** {choice(database['truths'])}" 
	await ctx.send(response)

@client.command(aliases = ['d'])
@commands.cooldown(1, 3, BucketType.user)
async def dare(ctx):
	"""Get a dare."""
	
	response = f"**Dare:** {choice(database['dares'])}" 
	await ctx.send(response)

@client.command(aliases = ['neverhaveiever', 'nhie', 'ever', 'n'])
@commands.cooldown(1, 2.5, BucketType.user)
async def never(ctx):
	"""Get a never have I ever question."""
	
	response = f"**Never have I ever** {choice(database['nhie'])}" 
	await ctx.send(response)

@client.command(aliases = ['tot', 'tt'])
@commands.cooldown(1, 2.5, BucketType.user)
async def thisorthat(ctx):
	"""Get a this or that question."""
	
	response = choice(database['tot'])
	
	message = []
	# check if the question has a title.
	if ':' in response: 
		split = response.split(':')
		message.append(f"**{split[0]}**")  
		tort = split[1].strip()
	else:
		tort = response
	message.append(f"🔴 {tort.replace(' or ', ' **OR** ')} 🔵")
	
	embed = discord.Embed(
		color = choice((COLOR_RED, COLOR_BLUE)),
		timestamp = datetime.utcnow(),
		description = '\n'.join(message)
	)

	sent_embed = await ctx.send(embed = embed)
	await sent_embed.add_reaction("🔴")
	await sent_embed.add_reaction("🔵")

@client.command(aliases = ['wyr', 'rather'])
@commands.cooldown(1, 3, BucketType.user)
async def wouldyourather(ctx):
	"""Get a would you rather question."""
	
	async with CLIENT_SESSION.get('http://either.io/questions/next/1/') as resp:
		result = await resp.json(content_type = None)
		result = result['questions'][0]

	option1, option2 = result['option_1'].capitalize(), result['option_2'].capitalize()
	option1_total, option2_total = int(result['option1_total']), int(result['option2_total'])
	option_total, comments = option1_total + option2_total, result['comment_total']
	title, desc, url = result['title'], result['moreinfo'], result['short_url']
	
	embed = discord.Embed(
		title = title,
		url = url,
		color = COLOR_RED if (option1_total > option2_total) else COLOR_BLUE,
		timestamp = datetime.utcnow()
	)
	embed.add_field(
		name = 'Would You Rather',
		value = f"🔴 `({(option1_total / option_total * 100):.1f}%)` {option1}\n🔵 `({(option2_total / option_total * 100):.1f}%)` {option2}",
		inline = False
	)
	if desc: embed.add_field(name = "More Info", value = desc, inline = False)
	embed.set_footer(text = f"either.io • 💬 {comments}")
	sent_embed = await ctx.send(embed = embed)
	await sent_embed.add_reaction("🔴")
	await sent_embed.add_reaction("🔵")
	
@client.command(aliases = ['wyp', 'button'])
@commands.cooldown(1, 3, BucketType.user)
async def willyoupressthebutton(ctx):
	"""Get a will you press the button question."""
	
	async with CLIENT_SESSION.post('https://api2.willyoupressthebutton.com/api/v2/dilemma') as resp:
		result = await resp.json(content_type = None)
		result = result['dilemma']

	txt1, txt2 = html.unescape(result['txt1']), html.unescape(result['txt2'])
	will_press, wont_press = int(result['yes']), int(result['no'])
	press_total, q_id = (will_press + wont_press), result['id']
	url = f"https://willyoupressthebutton.com/{q_id}"
	
	embed = discord.Embed(
		title = "Press the button?",
		url = url,
		color = COLOR_RED if (will_press > wont_press) else COLOR_BLUE,
		timestamp = datetime.utcnow()
	)
	embed.add_field(
		name = 'Will you press the button if...',
		value = f"{txt1}\n**but...**\n{txt2}",
		inline = False
	)
	embed.add_field(
		name = 'Options',
		value = f"🔴 `({(will_press / press_total * 100):.1f}%)` I will press the button.\n🔵 `({(wont_press / press_total * 100):.1f}%)` I won't press the button.",
		inline = False
	)
	embed.set_footer(text = "willyoupressthebutton.com")
	sent_embed = await ctx.send(embed = embed)
	await sent_embed.add_reaction("🔴")
	await sent_embed.add_reaction("🔵")

## Login.
keep_alive.keep_alive()
client.run(os.getenv("TOKEN"))
