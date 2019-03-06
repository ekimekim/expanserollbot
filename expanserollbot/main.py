
import discord
import pyhedrals


client = discord.client()
dispatch = {}
roller = pyhedrals.DiceRoller()


def register(fn):
	dispatch[fn.__name__] = fn
	return fn


async def reply(message, fmt, *args, **kwargs):
	await client.send_message(message.channel, fmt.format(*args, **kwargs))


@register
async def ping(message):
	await reply(message, 'pong')


@register
async def roll(message):
	body = ' '.join(message.content.split(' ')[1:])
	try:
		result = roller.parse(body)
	except Exception as e:
		await reply(message, "Error: {}", e)
		return
	roll_strings = ' | '.join(roller.getRollStrings())
	if len(roll_strings) > 200:
		roll_strings = "lots of dice"
	await reply(message, "{m.author.name} rolled {}: [{}] {}", body, roll_strings, result, m=message)


@client.event
async def on_message(message):
	if not message.content:
		return
	command = message.content.split()[0]
	if command in dispatch:
		await dispatch[command](message)


def main(token):
	client.run(token)
