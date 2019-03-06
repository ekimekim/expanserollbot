
import logging

import discord
import pyhedrals


client = discord.Client()
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
	await reply(message, "{m.author.name} rolled {}: [{}] = {}", body, roll_strings, result, m=message)


@client.event
async def on_message(message):
	logging.debug("Got message: {}".format(message.content))
	if not message.content:
		return
	command = message.content.split()[0].lstrip('!')
	if command in dispatch:
		logging.debug("Dispatching to {}".format(dispatch[command]))
		await dispatch[command](message)


def main(token):
	client.run(token)
