#!/usr/bin/env python

# Channel statistics script (originally from altkeeper)
# Author: Blake Oliver <oliver22213@me.com>


# this script expects a few environment variables to be set:
# stats_for_name: the name of the character statistics are being requested for. Leave it out if general stats are requested, rather than for a specific person.
# stats_for_obj: the database object of the character statistics are being requested for (E.G. #123). Can be left out of general stats are requested.
# for_channel: Either the name of a channel in allowed_channels or 'all'.
# database_path: the path to a valid SQLite3 database file, relative to the location of this script, or starting from the root.
# allowed_channels: a json list of channel IDs the requester has access to.
# total_channels: The total number of channels that currently exist.


import dernan_core

import os
import sys


def channel_stats(db, forname, forobj, chan, total_chans):
	"""Return channel statistics."""
	if chan == None:
		return """Show statistics for what channel?"""
	s = db.sessionmaker()
	sender = forobj
	prefix = ""
	total_messages = db.total_channel_messages(s)
	if chan == 'all': # return all channel statistics
		if forobj == None:
			# For all channels, but no specific person.
			return """There are a total of {} messages in the database, across {} distinct channels.""".format(total_messages, total_chans)
		else:
			# For a specific person on all channels
			total_messages_from_sender = db.total_channel_messages_from_sender_obj(s, forobj)
			last_hour = db.total_channel_messages_from_sender_obj(s, forobj, hours=1)
			last_day = db.total_channel_messages_from_sender_obj(s, forobj, days=1)
			last_week = db.total_channel_messages_from_sender_obj(s, forobj, days=7)
			percent_of_total = round(100*float(total_messages_from_sender)/float(total_messages), 2)
			return """There are a total of {} channel messages in the database, {} of which are from {} across all channels ({}%). {} of those were sent in the past hour, {} in the past day, and {} in the past week.""".format(total_messages, total_messages_from_sender, forname, percent_of_total, last_hour, last_day, last_week)
	elif chan != 'all':
		if forobj != None:
			# A sender on a specific channel
			total_messages_for_chan = db.total_channel_messages_to_channel(s, chan)
			total_messages_from_sender_to_chan = db.total_channel_messages_from_sender_obj_to_channel(s, chan, forobj)
			if total_messages_from_sender_to_chan == 0:
				return """{}{} hasn't sent any messages to channel {}.""".format(prefix, forname, chan)
			last_hour = db.total_channel_messages_from_sender_obj_to_channel(s, chan, forobj, hours=1)
			last_day = db.total_channel_messages_from_sender_obj_to_channel(s, chan, sender, days=1)
			last_week = db.total_channel_messages_from_sender_obj_to_channel(s, chan, sender, days=7)
			percent_of_total = round(100*float(total_messages_from_sender_to_chan)/float(total_messages_for_chan), 2)
			return """{}There are {} messages to {} in the database, {} of which are from {} ({}%). {} of those were sent in the last hour, {} in the last day, and {} in the last week.""".format(prefix, total_messages_for_chan, chan, total_messages_from_sender_to_chan, forname, percent_of_total, last_hour, last_day, last_week)
		else:
			# stats for a specific channel, but no specific person
			total_messages_for_chan = db.total_channel_messages_to_channel(s, chan)
			if total_messages_for_chan == 0:
				return """No messages in the database for channel {}.""".format(chan)
			last_hour = db.total_channel_messages_to_channel(s, chan, hours=1)
			last_day = db.total_channel_messages_to_channel(s, chan, days=1)
			last_week = db.total_channel_messages_to_channel(s, chan, days=7)
			percent = round(100*float(total_messages_for_chan)/float(total_messages), 2)
			return """{}There are {} total channel messages in the database, {} of which are to channel {} ({}%). {} of those were sent in the last hour, {} in the last day, and {} in the last week.""".format(prefix, total_messages, total_messages_for_chan, chan, percent, last_hour, last_day, last_week)


if __name__ == '__main__':
	db_path = os.getenv("database_path", '/home/yourusername/moo/yourmoo/files/databases/channels.db')
	stats_for_name = os.getenv("stats_for_name")
	stats_for_obj = os.getenv("stats_for_obj")
	for_channel = os.getenv("for_channel")
	#allowed_channels = json.loads(os.getenv("allowed_channels"))
	total_channels = int(os.getenv("total_channels"))
	db = dernan_core.ChannelDatabase(db_path, dernan_core.coms_base)
	r = channel_stats(db, stats_for_name, stats_for_obj, for_channel, total_channels)
	sys.stdout.write(r+"\r\n")
	sys.stdout.flush()
