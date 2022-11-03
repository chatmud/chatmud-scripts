# dernan core - various classes and functions useful in more than one of my scripts
# Author: Blake Oliver (dernan) <oliver22213@me.com>

import datetime
import time
import calendar
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, ForeignKey, Column, func, types
from sqlalchemy import Enum as SAEnum
import os
import operator
import random

coms_base = declarative_base()
altkeeper_coms_base = declarative_base()
datetime_format_string = "%A, %B %d, %Y. At %I:%M %p"


class Database(object):
	def __init__(self, db_name, base):
		self.db_name = db_name
		self.base = base
		self.db = None
		if not os.path.isfile(self.db_name):
			self.create_database(self.db_name)
		else:
			self.load_database(self.db_name)

	def setup(self, database):
		self.db = create_engine("sqlite:///{}".format(database))
		self.db.echo = False #Logging disabled
		self.sessionmaker = sessionmaker(bind=self.db)

	def create_database(self, database):
		self.setup(database)
		self.base.metadata.create_all(self.db)

	def load_database(self, database):
		self.setup(database)

class ChannelDatabase(Database):
	# stripped down API, because adding messages isn't the purpose of this script

	def total_channel_messages(self, session, **kwargs):
		"""Return the total number of channel messages in the database.
All keyword arguments are assumed to represent a period of time (until now) for which the number of total messages should be returned; they are passed to datetime.timedelta.
To retrieve the number of channel messages for the past 6 hours, you just pass hours=6; for the past 3 days and 6 hours, days=3, hours=6.
If you want the total without a timeframe, don't include any keyword arguments.
		"""
		if kwargs: # We were given a timeframe to get the total number of messages for, up until now
			timeframe = time.mktime((datetime.datetime.utcnow() - datetime.timedelta(**kwargs)).timetuple())
			c = session.query(ChannelMessage).filter(ChannelMessage.time>=timeframe).count()
		else: # no timeframe, get the complete total
			c = session.query(ChannelMessage).count()
		return c

	def total_channel_messages_from_sender(self, session, sender, **kwargs):
		"""Return the total number of messages from the given sender.
sender can either be a string (a single name to get the total for), or a list of strings (get the total for all of the names).
All keyword arguments are assumed to represent a period of time (until now) for which the number of total messages should be returned; they are passed to datetime.timedelta.
To retrieve the number of channel messages from sender for the past 6 hours, you just pass hours=6; for the past 3 days and 6 hours, days=3, hours=6.
If you want the total without a timeframe, don't include any keyword arguments.
		"""
		query = session.query(ChannelMessage) # base query
		if type(sender) == str:
			sender = sender.title()
			query = query.filter(ChannelMessage.sender_name.ilike(sender)) # filter the query for messages by one sender
		elif type(sender) == list:
			sender = [s.title() for s in sender]
			query = query.filter(ChannelMessage.sender_name.in_(sender))
		if kwargs: # We were given a timeframe to get the total number of messages for, up until now
			timeframe = time.mktime((datetime.datetime.now() - datetime.timedelta(**kwargs)).timetuple())
			query = query.filter(ChannelMessage.time>=timeframe)
		# now that all filters that have been requested have been applied...
		c = query.count()
		return c

	def total_channel_messages_from_sender_obj(self, session, sender, **kwargs):
		"""Return the total number of messages from the given sender's object.
All keyword arguments are assumed to represent a period of time (until now) for which the number of total messages should be returned; they are passed to datetime.timedelta.
To retrieve the number of channel messages from sender for the past 6 hours, you just pass hours=6; for the past 3 days and 6 hours, days=3, hours=6.
If you want the total without a timeframe, don't include any keyword arguments.
		"""
		query = session.query(ChannelMessage) # base query
		query = query.filter_by(sender_object = sender) # filter the query for messages by one sender's object
		if kwargs: # We were given a timeframe to get the total number of messages for, up until now
			timeframe = time.mktime((datetime.datetime.now() - datetime.timedelta(**kwargs)).timetuple())
			query = query.filter(ChannelMessage.time>=timeframe)
		# now that all filters that have been requested have been applied...
		c = query.count()
		return c

	def total_channel_messages_from_sender_to_channel(self, session, channel_name, sender, **kwargs):
		"""Return the number of messages sent to channel_name by sender.
sender can either be a string (a single name to get the total for), or a list of strings (get the total for all of the names).
All keyword arguments are assumed to represent a period of time (until now) for which the number of total messages should be returned; they are passed to datetime.timedelta.
To retrieve the number of replies from sender for the past 6 hours, you just pass hours=6; for the past 3 days and 6 hours, days=3, hours=6.
If you want the total without a timeframe, don't include any keyword arguments.
		"""
		channel_name = channel_name.lower()
		query = session.query(ChannelMessage).filter(ChannelMessage.channel_name==channel_name)
		if type(sender) == str:
			sender = sender.title()
			query = query.filter(ChannelMessage.sender_name.ilike(sender)) # filter the query for messages by one sender
		elif type(sender) == list:
			sender = [s.title() for s in sender]
			query = query.filter(ChannelMessage.sender_name.in_(sender))
		if kwargs:
			timeframe = time.mktime((datetime.datetime.now() - datetime.timedelta(**kwargs)).timetuple())
			query = query.filter(ChannelMessage.time>=timeframe)
		c = query.count()
		return c

	def total_channel_messages_from_sender_obj_to_channel(self, session, channel_name, sender, **kwargs):
		"""Return the number of messages sent to channel_name by sender.
All keyword arguments are assumed to represent a period of time (until now) for which the number of total messages should be returned; they are passed to datetime.timedelta.
To retrieve the number of messages from sender for the past 6 hours, you just pass hours=6; for the past 3 days and 6 hours, days=3, hours=6.
If you want the total without a timeframe, don't include any keyword arguments.
		"""
		channel_name = channel_name.lower()
		query = session.query(ChannelMessage).filter_by(sender_object = sender, channel_name=channel_name)
		if kwargs:
			timeframe = time.mktime((datetime.datetime.now() - datetime.timedelta(**kwargs)).timetuple())
			query = query.filter(ChannelMessage.time>=timeframe)
		c = query.count()
		return c

	def total_channel_messages_to_channel(self, session, channel_name, **kwargs):
		"""Return the total number of messages to a given channel in the database.
All keyword arguments are assumed to represent a period of time (until now) for which the number of total messages should be returned; they are passed to datetime.timedelta.
To retrieve the number of channel messages to the given channel for the past 6 hours, you just pass hours=6; for the past 3 days and 6 hours, days=3, hours=6.
If you want the total without a timeframe, don't include any keyword arguments.
		"""
		channel_name = channel_name.lower()
		if kwargs:
			timeframe = time.mktime((datetime.datetime.now() - datetime.timedelta(**kwargs)).timetuple())
			c = session.query(ChannelMessage).filter(ChannelMessage.channel_name==channel_name, ChannelMessage.time>=timeframe).count()
		else:
			c = session.query(ChannelMessage).filter_by(channel_name=channel_name).count()
		return c

	def get_channel_name_from_partial(self, session, partial, verbose=False):
		"""Given a session and a partial channel name, return a tuple of the form (channelname, prefix) if there is at least one message in the database who's name matches the partial given. Return a tuple of (None, "") otherwise.
Prefix just says that there aren't any messages from <partialname> in the database, assuming you meant <channelname>.
		"""
		chan = None
		if self.total_channel_messages_to_channel(session, partial) == 0: # no messages to the given channel in the database
			# check if the name given is a partial one, and if so get the name of the first channel in the db that has a name like it
			names_like = session.query(ChannelMessage).filter(ChannelMessage.channel_name.ilike("""{}%""".format(partial))).count()
			if names_like: # at least one row with a channel name like the one given
				chan = session.query(ChannelMessage).filter(ChannelMessage.channel_name.ilike("""{}%""".format(partial))).limit(1).one().channel_name
				if verbose:
					prefix = """(No messages to channel {} in the database, assuming you mean {}.) """.format(partial, chan)
				else:
					prefix = ""
			else:
				prefix = ""
		else: # there is at least one message from the given channel in the database
			prefix = ""
		return chan, prefix

	def get_top_talkers_for_channel(self, session, channel_name, limit):
		"""Given a session, a full channel name, and a limit, return a sorted list of the players with the most messages on the given channel; each list item is a tuple of form (name, count), with as many as limit items. The list is sorted with the highest first. if the given channel name is "all", top talkers across all channels are returned in the same format."""
		# build a list of (playername, total_messages) tuples using sqlalchemy (this is waaay faster than manually doing it)
		if channel_name == 'all':
			q=session.query(ChannelMessage.sender_name.distinct(), func.count(ChannelMessage.sender_name)).group_by(ChannelMessage.sender_name)
		else:
			q=session.query(ChannelMessage.sender_name.distinct(), func.count(ChannelMessage.sender_name)).filter_by(channel_name=channel_name).group_by(ChannelMessage.sender_name)
		top = sorted(q.all(), key=operator.itemgetter(1), reverse=True)
		return top[:limit]

	def get_top_channels(self, session, limit):
		"""Given a session and a limit, return a list of channels that have the most messages; each item in the returned list is a tuple of the form (channel_name, total_messages). The list is sorted from highest number of messages to lowest."""
		q=session.query(ChannelMessage.channel_name.distinct(), func.count(ChannelMessage.message)).group_by(ChannelMessage.channel_name)
		top = sorted(q.all(), key=operator.itemgetter(1), reverse=True)
		return top[:limit]

	def write_log(self, session, filehandle, channel_name, start_time=None, end_time=None, limit=10000, line_ending="\r\n"):
		"""Output a log of the last limit messages sent to channel_name to filehandle.
		Args and options:
			session: An SQLAlchemmy database session object that will be used for queries.
			filehandle: a file-like object to write() log lines to. Will not be closed; calling code must handle that.
			channel_name: the full name of the channel to write a log for.
			start_time: a datetime object which marks what point in time messages should be retrieved after. If this is none (the default), jan 1, 1970 is assumed.
			end_time: a datetime object to retrieve messages up to. If this is set to none (the default), it is set to the current time and date.
			limit: a limit of how many messages to retrieve.
			line_ending: characters which should be used for line endings.
"""
		if start_time == None:
			start_time = datetime.datetime(1970,1,1)
		if end_time == None:
			end_time = datetime.datetime.now()
		start_time = time.mktime(start_time.timetuple())
		end_time = time.mktime(end_time.timetuple())
		query = session.query(ChannelMessage).filter(ChannelMessage.channel_name==channel_name, ChannelMessage.time>=start_time, ChannelMessage.time<=end_time)
		if limit == None or limit == 0: # no limit
			messages = query.all()
		else:
			messages = query.all()[-limit:]
		first = messages[0]
		last = messages[-1]
		start_date = first.timestamp.strftime(datetime_format_string)
		end_date = last.timestamp.strftime(datetime_format_string)
		prefix = """This log was pulled from Chat Mud's database for channel {}.{}It begins {}, and ends {} (all dates are in EST).""".format(channel_name, line_ending, start_date, end_date)
		filehandle.write(prefix+line_ending+line_ending)
		for cm in messages:
			datetime_string = cm.timestamp.strftime("%m/%d/%Y %I:%M:%S %p")
			l = """[{}] {}: {}{}""".format(datetime_string, cm.sender_name, cm.message, line_ending)
			filehandle.write(l)
		filehandle.write(line_ending+"Log ends.{}".format(line_ending))


	def add_altkeeper_message(self, s, m, sender_object="#-1", channel_id="imported_db", prefix=""):
		"""Given a db session and a `ChannelMessage` following altkeeper's database schema, add it to this database.
Note that this method does *NOT* commit it's changes to the database, as (when this method is called many times in succession) it would cause lots of writes to disk for little benefit.
You can optionally provide sender_object, channel_id, and prefix as arguments, in which case they override the defaults.
	"""
		prepped_msg = ChannelMessage(channel_name=m.channel_name, channel_id=channel_id, sender_name=m.sender, sender_object=sender_object, prefix = prefix, message=m.message, social='', verbatim=False, time=calendar.timegm(m.timestamp.timetuple()))
		s.add(prepped_msg)
		return True


# altkeeper class, for use in conversion scripts and any other tools that need to work with keeper's coms database

class AltkeeperComsDatabase(Database):
	"""Database that stores channel messages, tells, and any other future forms of communications that should be logged."""

	def add_channel_message(self, session, channel_name, sender, message, timestamp=None):
		"""Add an individual message to the database, optionally providing a timestamp. If one isn't provided, the current time is used."""
		m = AltkeeperChannelMessage(channel_name, sender.lower(), message, timestamp)
		session.add(m)
		session.commit()

	def add_tell_message(self, session, *args, **kwargs):
		"""A wrapper that, given a session bound to a database engine will create a AltkeeperTellMessage instance with the given args and kwargs and commit it."""
		m = AltkeeperTellMessage(*args, **kwargs)
		session.add(m)
		session.commit()

	def total_channel_messages(self, session, **kwargs):
		"""Return the total number of channel messages in the database.
All keyword arguments are assumed to represent a period of time (until now) for which the number of total messages should be returned; they are passed to datetime.timedelta.
To retrieve the number of channel messages for the past 6 hours, you just pass hours=6; for the past 3 days and 6 hours, days=3, hours=6.
If you want the total without a timeframe, don't include any keyword arguments.
		"""
		if kwargs: # We were given a timeframe to get the total number of messages for, up until now
			timeframe = (datetime.datetime.utcnow() - datetime.timedelta(**kwargs))
			c = session.query(AltkeeperChannelMessage).filter(AltkeeperChannelMessage.timestamp>=timeframe).count()
		else: # no timeframe, get the complete total
			c = session.query(AltkeeperChannelMessage).count()
		return c

	def total_tell_messages(self, session, **kwargs):
		"""Return the total number of tell messages in the database.
All keyword arguments are assumed to represent a period of time (until now) for which the number of total messages should be returned; they are passed to datetime.timedelta.
To retrieve the number of tell messages for the past 6 hours, you just pass hours=6; for the past 3 days and 6 hours, days=3, hours=6.
If you want the total without a timeframe, don't include any keyword arguments.
		"""
		if kwargs: # We were given a timeframe to get the total number of messages for, up until now
			timeframe = (datetime.datetime.utcnow() - datetime.timedelta(**kwargs))
			c = session.query(AltkeeperTellMessage).filter(AltkeeperTellMessage.timestamp>=timeframe).count()
		else:
			c = session.query(AltkeeperTellMessage).count()
		return c

	def total_channel_messages_from_sender(self, session, sender, **kwargs):
		"""Return the total number of messages from the given sender.
sender can either be a string (a single name to get the total for), or a list of strings (get the total for all of the names).
All keyword arguments are assumed to represent a period of time (until now) for which the number of total messages should be returned; they are passed to datetime.timedelta.
To retrieve the number of channel messages from sender for the past 6 hours, you just pass hours=6; for the past 3 days and 6 hours, days=3, hours=6.
If you want the total without a timeframe, don't include any keyword arguments.
		"""
		query = session.query(AltkeeperChannelMessage) # base query
		if type(sender) == str:
			sender = sender.lower()
			query = query.filter(AltkeeperChannelMessage.sender==sender) # filter the query for messages by one sender
		elif type(sender) == list:
			sender = [s.lower() for s in sender]
			query = query.filter(AltkeeperChannelMessage.sender.in_(sender))
		if kwargs: # We were given a timeframe to get the total number of messages for, up until now
			timeframe = (datetime.datetime.utcnow() - datetime.timedelta(**kwargs))
			query = query.filter(AltkeeperChannelMessage.timestamp>=timeframe)
		# now that all filters that have been requested have been applied...
		c = query.count()
		return c

	def total_tell_messages_from_sender(self, session, sender, **kwargs):
		"""Return the total number of tells from a given sender.
sender can either be a string (a single name to get the total for), or a list of strings (get the total for all of the names).
All keyword arguments are assumed to represent a period of time (until now) for which the number of total messages should be returned; they are passed to datetime.timedelta.
To retrieve the number of tell messages from sender for the past 6 hours, you just pass hours=6; for the past 3 days and 6 hours, days=3, hours=6.
If you want the total without a timeframe, don't include any keyword arguments.
		"""
		query = session.query(AltkeeperTellMessage)
		if type(sender) == str:
			sender = sender.lower()
			query = query.filter(AltkeeperTellMessage.sender==sender) # filter the query for messages by one sender
		elif type(sender) == list:
			sender = [s.lower() for s in sender]
			query = query.filter(AltkeeperTellMessage.sender.in_(sender))
		if kwargs:
			timeframe = (datetime.datetime.utcnow() - datetime.timedelta(**kwargs))
			query = query.filter(AltkeeperTellMessage.timestamp>=timeframe)
		c = query.count()
		return c

	def total_replies_from_sender(self, session, sender, **kwargs):
		"""Return the total number of tells that are actually replies from a given sender.
sender can either be a string (a single name to get the total for), or a list of strings (get the total for all of the names).
All keyword arguments are assumed to represent a period of time (until now) for which the number of total messages should be returned; they are passed to datetime.timedelta.
To retrieve the number of replies from sender for the past 6 hours, you just pass hours=6; for the past 3 days and 6 hours, days=3, hours=6.
If you want the total without a timeframe, don't include any keyword arguments.
		"""
		query = session.query(AltkeeperTellMessage).filter(AltkeeperTellMessage.is_reply==true)
		if type(sender) == str:
			sender = sender.lower()
			query = query.filter(AltkeeperTellMessage.sender==sender) # filter the query for messages by one sender
		elif type(sender) == list:
			sender = [s.lower() for s in sender]
			query = query.filter(AltkeeperTellMessage.sender.in_(sender))
		if kwargs:
			timeframe = (datetime.datetime.utcnow() - datetime.timedelta(**kwargs))
			query = query.filter(AltkeeperTellMessage.timestamp>=timeframe)
		c = query.count()
		return c

	def total_channel_messages_from_sender_to_channel(self, session, channel_name, sender, **kwargs):
		"""Return the number of messages sent to channel_name by sender.
sender can either be a string (a single name to get the total for), or a list of strings (get the total for all of the names).
All keyword arguments are assumed to represent a period of time (until now) for which the number of total messages should be returned; they are passed to datetime.timedelta.
To retrieve the number of replies from sender for the past 6 hours, you just pass hours=6; for the past 3 days and 6 hours, days=3, hours=6.
If you want the total without a timeframe, don't include any keyword arguments.
		"""
		channel_name = channel_name.lower()
		query = session.query(AltkeeperChannelMessage).filter(AltkeeperChannelMessage.channel_name==channel_name)
		if type(sender) == str:
			sender = sender.lower()
			query = query.filter(AltkeeperChannelMessage.sender==sender) # filter the query for messages by one sender
		elif type(sender) == list:
			sender = [s.lower() for s in sender]
			query = query.filter(AltkeeperChannelMessage.sender.in_(sender))
		if kwargs:
			timeframe = (datetime.datetime.utcnow() - datetime.timedelta(**kwargs))
			query = query.filter(AltkeeperChannelMessage.timestamp>=timeframe)
		c = query.count()
		return c

	def total_tell_messages_from_sender_to_receiver(self, session, sender, receiver, **kwargs):
		"""Return the total number of tells from a given sender to a given receiver.
All keyword arguments are assumed to represent a period of time (until now) for which the number of total messages should be returned; they are passed to datetime.timedelta.
To retrieve the number of tells from sender to receiver for the past 6 hours, you just pass hours=6; for the past 3 days and 6 hours, days=3, hours=6.
If you want the total without a timeframe, don't include any keyword arguments.
		"""
		sender = sender.lower()
		receiver = receiver.lower()
		if kwargs:
			timeframe = (datetime.datetime.utcnow() - datetime.timedelta(**kwargs))
			c = session.query(AltkeeperTellMessage).filter(AltkeeperTellMessage.sender==sender, AltkeeperTellMessage.receiver==receiver, AltkeeperTellMessage.timestamp>=timeframe).count()
		else:
			c = session.query(AltkeeperTellMessage).filter_by(sender=sender, receiver=receiver).count()
		return c

	def total_channel_messages_to_channel(self, session, channel_name, **kwargs):
		"""Return the total number of messages to a given channel in the database.
All keyword arguments are assumed to represent a period of time (until now) for which the number of total messages should be returned; they are passed to datetime.timedelta.
To retrieve the number of channel messages to the given channel for the past 6 hours, you just pass hours=6; for the past 3 days and 6 hours, days=3, hours=6.
If you want the total without a timeframe, don't include any keyword arguments.
		"""
		channel_name = channel_name.lower()
		if kwargs:
			timeframe = (datetime.datetime.utcnow() - datetime.timedelta(**kwargs))
			c = session.query(AltkeeperChannelMessage).filter(AltkeeperChannelMessage.channel_name==channel_name, AltkeeperChannelMessage.timestamp>=timeframe).count()
		else:
			c = session.query(AltkeeperChannelMessage).filter_by(channel_name=channel_name).count()
		return c

	def total_tell_messages_to_receiver(self, session, receiver, **kwargs):
		"""Return the total number of tells sent to a given receiver.
All keyword arguments are assumed to represent a period of time (until now) for which the number of total messages should be returned; they are passed to datetime.timedelta.
To retrieve the number of tell messages to the given receiver for the past 6 hours, you just pass hours=6; for the past 3 days and 6 hours, days=3, hours=6.
If you want the total without a timeframe, don't include any keyword arguments.
		"""
		receiver = receiver.lower()
		if kwargs:
			timeframe = (datetime.datetime.utcnow() - datetime.timedelta(**kwargs))
			c = session.query(AltkeeperTellMessage).filter(AltkeeperTellMessage.receiver==receiver, AltkeeperTellMessage.timestamp>=timeframe).count()
		else:
			c = session.query(AltkeeperTellMessage).filter_by(receiver=receiver).count()
		return c

	def get_channel_messages(self, session, channel_name, sender, limit=None):
		"""Return a list of database model instances that were sent by the provided name on the provided channel."""
		sender = sender.lower()
		channel_name = channel_name.lower()
		c = session.query(AltkeeperChannelMessage).filter_by(sender = sender, channel_name = channel_name).order_by(AltkeeperChannelMessage.timestamp)
		if limit != None:
			return c[-limit:] # return the last limit messages
		else:
			return c.all()

	def get_channel_name_from_partial(self, session, partial, verbose=False):
		"""Given a session and a partial channel name, return a tuple of the form (channelname, prefix) if there is at least one message in the database who's name matches the partial given. Return a tuple of (None, "") otherwise.
Prefix just says that there aren't any messages from <partialname> in the database, assuming you meant <channelname>.
		"""
		chan = None
		if self.total_channel_messages_to_channel(session, partial) == 0: # no messages to the given channel in the database
			# check if the name given is a partial one, and if so get the name of the first channel in the db that has a name like it
			names_like = session.query(AltkeeperChannelMessage).filter(AltkeeperChannelMessage.channel_name.ilike("""{}%""".format(partial))).count()
			if names_like: # at least one row with a channel name like the one given
				chan = session.query(AltkeeperChannelMessage).filter(AltkeeperChannelMessage.channel_name.ilike("""{}%""".format(partial))).limit(1).one().channel_name
				if verbose:
					prefix = """(No messages to channel {} in the database, assuming you mean {}.) """.format(partial, chan)
				else:
					prefix = ""
			else:
				prefix = ""
		else: # there is at least one message from the given channel in the database
			# messages were found to a channel with the given name
			chan = partial
			prefix = ""
		return chan, prefix

	def get_top_talkers_for_channel(self, session, channel_name, limit):
		"""Given a session, a full channel name, and a limit, return a sorted list of the players with the most messages on the given channel; each list item is a tuple of form (name, count), with as many as limit items. The list is sorted with the highest first. if the given channel name is "all", top talkers across all channels are returned in the same format."""
		# build a list of (playername, total_messages) tuples using sqlalchemy (this is waaay faster than manually doing it)
		if channel_name == 'all':
			q=session.query(AltkeeperChannelMessage.sender.distinct(), func.count(AltkeeperChannelMessage.sender)).group_by(ChannelMessage.sender)
		else:
			q=session.query(AltkeeperChannelMessage.sender.distinct(), func.count(AltkeeperChannelMessage.sender)).filter_by(channel_name=channel_name).group_by(AltkeeperChannelMessage.sender)
		top = sorted(q.all(), key=operator.itemgetter(1), reverse=True)
		return top[:limit]

	def get_top_channels(self, session, limit):
		"""Given a session and a limit, return a list of channels that have the most messages; each item in the returned list is a tuple of the form (channel_name, total_messages). The list is sorted from highest number of messages to lowest."""
		q=session.query(AltkeeperChannelMessage.channel_name.distinct(), func.count(AltkeeperChannelMessage.message)).group_by(AltkeeperChannelMessage.channel_name)
		top = sorted(q.all(), key=operator.itemgetter(1), reverse=True)
		return top[:limit]

	def write_log(self, session, filehandle, channel_name, start_time=None, end_time=None, limit=10000, line_ending="\r\n"):
		"""Output a log of the last limit messages sent to channel_name to filehandle.
		Args and options:
			session: An SQLAlchemmy database session object that will be used for queries.
			filehandle: a file-like object to write() log lines to. Will not be closed; calling code must handle that.
			channel_name: the full name of the channel to write a log for.
			start_time: a datetime object which marks what point in time messages should be retrieved after. If this is none (the default), jan 1, 1970 is assumed.
			end_time: a datetime object to retrieve messages up to. If this is set to none (the default), it is set to the current time and date.
			limit: a limit of how many messages to retrieve.
			line_ending: characters which should be used for line endings.
"""
		if start_time == None:
			start_time = datetime.datetime(1970,1,1)
		if end_time == None:
			end_time = datetime.datetime.utcnow()
		query = session.query(AltkeeperChannelMessage).filter(AltkeeperChannelMessage.channel_name==channel_name, AltkeeperChannelMessage.timestamp>=start_time, AltkeeperChannelMessage.timestamp<=end_time)
		if limit == None or limit == 0: # no limit
			messages = query.all()
		else:
			messages = query.all()[-limit:]
		first = messages[0]
		last = messages[-1]
		start_date = first.timestamp.strftime(datetime_format_string)
		end_date = last.timestamp.strftime(datetime_format_string)
		prefix = """This log was pulled from altkeeper's database for channel {}.{}It begins {}, and ends {} (all dates are in universal coordinated time).""".format(channel_name, line_ending, start_date, end_date)
		filehandle.write(prefix+line_ending+line_ending)
		for cm in messages:
			datetime_string = cm.timestamp.strftime("%m/%d/%Y %I:%M:%S %p")
			l = """[{}] {}: {}{}""".format(datetime_string, cm.sender, cm.message, line_ending)
			filehandle.write(l)
		filehandle.write(line_ending+"Log ends.{}".format(line_ending))



class ChannelMessage(coms_base):
	__tablename__ = 'history'
	rowid = Column(types.Integer, primary_key=True)
	channel_name = Column(types.VARCHAR(15), nullable=False)
	channel_id = Column(types.VARCHAR(64), nullable=False)
	sender_name = Column(types.VARCHAR(30))
	sender_object = Column(types.VARCHAR(7))
	prefix = Column(types.VARCHAR(30))
	message = Column(types.TEXT, nullable=False)
	social = Column(types.BLOB, server_default='')
	verbatim = Column(types.Boolean)
	time = Column(types.REAL, nullable=False)

class AltkeeperChannelMessage(altkeeper_coms_base):
	__tablename__ = 'channel_messages'
	id = Column(types.Integer, primary_key=True)
	channel_name = Column(types.String(15), nullable=False)
	sender = Column(types.String(15), nullable=False)
	message = Column(types.String(512))
	timestamp = Column(types.DateTime)

	def __init__(self, channel_name, sender, message, timestamp=None):
		"""A single message instance sent to a channel."""
		self.channel_name = channel_name
		self.sender = sender
		self.message = message
		self.timestamp = timestamp
		if self.timestamp == None:
			self.timestamp = datetime.datetime.utcnow()

	def __repr__(self):
		return """<Channel message from {} to channel {}: {}>""".format(self.sender, self.channel_name, self.message)

class AltkeeperTellMessage(altkeeper_coms_base):
	__tablename__ = 'tell_messages'
	id = Column(types.Integer, primary_key=True)
	sender = Column(types.String(15), nullable=False)
	receiver = Column(types.String(15), nullable=False)
	message = Column(types.String(512))
	is_reply = Column(types.Boolean)
	timestamp = Column(types.DateTime)

	def __init__(self, sender, receiver, message, is_reply=False, timestamp=None):
		"""A single tell message instance."""
		self.sender = sender.lower()
		self.receiver = receiver.lower() # in case I log tells to other characters
		self.message = message
		self.is_reply = is_reply
		self.timestamp = timestamp
		if self.timestamp == None:
			self.timestamp = datetime.datetime.utcnow()

	def __repr__(self):
		return """<Tell message from {} to {}: {}>""".format(self.sender, self.receiver, self.message)
