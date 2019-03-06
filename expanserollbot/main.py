
import logging
import random
from collections import Counter

import discord
import pyhedrals


client = discord.Client()
dispatch = {}
roller = pyhedrals.DiceRoller()

RED_DICE = [
	"<:diered1:552828733430693898>",
	"<:diered2:552828733354934278>",
	"<:diered3:552828733451403265>",
	"<:diered4:552828733594271792>",
	"<:diered5:552828733782884362>",
	"<:diered6:552828733787078656>",
]

PURPLE_DICE = [
	"<:diepurple1:552828732998418459>",
	"<:diepurple2:552828733841473536>",
	"<:diepurple3:552828734311497748>",
	"<:diepurple4:552828733426237441>",
	"<:diepurple5:552828733036167190>",
	"<:diepurple6:552828733485219840>",
]

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
	if body:
		try:
			bonus = int(body)
		except ValueError:
			await reply(message, "I don't understand. Syntax: !test <bonus or penalty>, eg. !test -1")
			return
	else:
		bonus = 0
	# last roll is drama die
	rolls = [random.randint(1, 6) for _ in range(3)]
	result = sum(rolls) + bonus
	roll1, roll2, drama = rolls
	stunt = max(Counter(rolls).values()) > 1
	# formatting
	
	main_response = "{r[0]} + {r[1]} + {r[2]}{bonus} = **{result}**".format(
		r=[RED_DICE[roll1-1], RED_DICE[roll2-1], PURPLE_DICE[drama-1]],
		result=result,
		bonus = ' + {}'.format(bonus) if bonus else '',
	)
	if stunt:
		full_response = "Stunt! {} and you can spend {} SP".format(main_response, drama)
	else:
		full_response = "{} with {} on the drama die".format(main_response, drama)
	await reply(message, "{}: {}", message.author.name, full_response)


@register
async def abilities(message):
	names = 'Acc', 'Con', 'Fight', 'Comm', 'Dex', 'Int', 'Per', 'Str', 'Will'
	lut = {
		3: -2,
		4: -1,
		5: -1,
		6: 0,
		7: 0,
		8: 0,
		9: 1,
		10: 1,
		11: 1,
		12: 2,
		13: 2,
		14: 2,
		15: 3,
		16: 3,
		17: 3,
		18: 4,
	}
	values = [sum(random.randint(1, 6) for _ in range(3)) for _ in names]
	output = ", ".join("{}: {} (rolled {})".format(n, lut[v], v) for n, v in zip(names, values))
	await reply(message, "{}: {}", message.author.name, output)


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
