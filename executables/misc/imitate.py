#!/usr/bin/env python

# imitate script
# Author: Blake Oliver <oliver22213@me.com>


# variables to tweak how this works


#min_imitation_threshold: the number of messages someone needs to have to a given channel before imitations will be possible
# setting this too low will give shitty imms;;
# setting it too high means it will take longer for someone who is new to a given channel to be imitated, but the quality of those imms will be better for it.
min_imitation_threshold = 300

# imitation_message_limit: How many messages to consider for imitations
# This is the maximum; if there are more messages than this, only this many will be considered when generating imms.
# setting this too low will give you shitty imitations until you change it, as with a low number it limits the amount of data used to generate them;
# setting this very high will give you better imitations up to a point, but with that many messages to process when creating them, it will take longer to generate an imm.
imitation_message_limit = 20000

# imitation_max_tries: The number of times the markov library will try to come up with an imitation when requested to do so.
# Setting this too low means people requesting an imitation will have to run the same command again to get one, if one wasn't found with the number of tries set;
# setting it very high doesn't have many consequences, other that it will take longer for an imitation to be generated when there is little data available on the given person and channel
imitation_max_tries = 200

# imitation_state_size: the state size for the markov algorithm
imitation_state_size = 2

# no_imitation_prefix_chars and no_imitation_suffix_chars: These are lists of characters that, if messages start or end with them, remove those messages from being used in imitations.
# These can be used for things like code evaluation on channels, commands to other bots, typo correcctions, etc
no_imitation_prefix_chars = ['/', '!', '.', ';']
no_imitation_suffix_chars = []


import dernan_core

import markovify
import os
import sys


def imitate(db, for_obj, for_name, for_chan):
	"""Given the object and name of a player that we have lots of messages for to a given channel, return a message that sounds like them."""
	prefix = ""
	s = db.sessionmaker()
	chan = for_chan
	tmtc = db.total_channel_messages_to_channel(s, chan) # total messages to channel
	if for_name != '*': # a specific person to imitate
		tsmtc = s.query(dernan_core.ChannelMessage).filter(dernan_core.ChannelMessage.channel_name==chan, dernan_core.ChannelMessage.sender_object == for_obj).count() # total sender messages to channel
	elif for_name == '*':
		tsmtc = None
	if for_name != '*':
		if tsmtc == 0: # no messages from name to channel name in the db
			return """There are No messages from {} to channel {}. I can't imitate someone who I don't have any messages from.""".format(for_name, chan)
		elif tsmtc < min_imitation_threshold:
			return """Sorry, {} must have at least {} messages to channel {} for me to imitate them well.""".format(for_name, min_imitation_threshold, chan)
	elif for_name == '*':
		if tmtc == 0:
			return """There are no messages to channel {}. I can't imitate a channel unless that channel has at least {} messages sent to it in total.""".format(chan, min_imitation_threshold)
		elif tmtc < min_imitation_threshold:
			return """Sorry, channel {} must have at least {} messages for me to imitate them well.""".format(for_name, min_imitation_threshold, chan)
	
	# let's imitate
	buffer = ""
	query = s.query(dernan_core.ChannelMessage).filter(dernan_core.ChannelMessage.channel_name == chan)
	if for_name != '*':
		query = query.filter(dernan_core.ChannelMessage.sender_object == for_obj)
	messages = query.order_by(dernan_core.ChannelMessage.time)[-imitation_message_limit:]
	for msg in messages:
		if msg.message != "":
			if not msg.message[0] in no_imitation_prefix_chars and not msg.message[-1] in no_imitation_suffix_chars:
				buffer += """{}\n""".format(msg.message)
	del(messages)
	model = markovify.NewlineText(buffer, state_size=imitation_state_size)
	sentence = model.make_sentence(tries=imitation_max_tries)
	if for_name == '*':
		name = "someone on {}".format(chan)
	if sentence == None:
		return """{}{} doesn't appear to have anything to say.""".format(prefix, for_name)
	else:
		return """{}{} says: {}""".format(prefix, for_name, sentence)

if __name__ == '__main__':
	db_path = os.getenv("database_path", '/home/yourusername/moo/yourmoo/files/databases/channels.db')
	for_name = os.getenv("for_name")
	for_obj = os.getenv("for_obj")
	for_channel = os.getenv("for_channel")
	db = dernan_core.ChannelDatabase(db_path, dernan_core.coms_base)
	r = imitate(db, for_obj, for_name, for_channel)
	sys.stdout.write(r+"\r\n")
	sys.stdout.flush()
