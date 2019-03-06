
import logging
import random
from collections import Counter

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


@register
async def test(message):
	"""Does a standard 3d6 + bonus ability test, identifying the drama die and stunt doubles."""
	body = ' '.join(message.content.split(' ')[1:])
	try:
		bonus = int(body)
	except ValueError:
		await reply(message, "I don't understand. Syntax: !test <bonus or penalty>, eg. !test -1")
		return
	# last roll is drama die
	rolls = [random.randint(1, 6) for _ in range(3)]
	result = sum(rolls) + bonus
	drama = rolls[-1]
	stunt = max(Counter(rolls).values()) > 1
	# formatting
	main_response = "*{r[0]}* + *{r[1]}* + __*{r[2]}*__ + {bonus} = **{result}**".format(
		r=rolls, bonus=bonus, result=result,
	)
	if stunt:
		full_response = "Stunt! {} and you can spend {} SP".format(main_response, drama)
	else:
		full_response = "{} with {} on the drama die".format(main_response, drama)
	await reply(message, "{}: {}", message.author.name, full_response)


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
