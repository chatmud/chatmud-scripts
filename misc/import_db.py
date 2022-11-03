# given a database using Chat Mud's schema, add it's entries to Chat Mud's database
# this is for use when importing prepared dumps of channels from other places
# Author: Blake Oliver <oliver22213@me.com>

import click
import dernan_core

@click.command(help="""Chatmud database import script, by Dernan

This is a script to import entries from a chatmud database into another; mainly used for importing prepared channel history from places other than chatmud.

Arguments:
import_source: the path to a database you would like to import. This won't be modified, but every entry in it's channel history table will be imported.
chatmud_database: the path to a chatmud database file; This is what entries will be added to.
""")
@click.argument('import_source', type=click.Path(exists=True, dir_okay=False))
@click.argument('chatmud_database', type=click.Path(exists=True, dir_okay=False, writable=True))
def import_db(import_source, chatmud_database):
	r = click.confirm("""Really import entries in '{}' to the chatmud database '{}'""".format(import_source, chatmud_database))
	if r:
		click.echo("Okay: importing.")
		cm_db = dernan_core.ChannelDatabase(chatmud_database, dernan_core.coms_base)
		cm_s = cm_db.sessionmaker() # open a session for the chatmud database
		starting_total_messages = cm_db.total_channel_messages(cm_s)
		starting_total_channels = cm_s.query(dernan_core.ChannelMessage.channel_name.distinct()).count()
		click.echo("Starting out with {} message(s) and {} channel(s) in the chatmud database.".format(starting_total_messages, starting_total_channels))
		i_db = dernan_core.ChannelDatabase(import_source, dernan_core.coms_base)
		i_s = i_db.sessionmaker() # open a session for the database to be imported
		click.echo("The database to be imported has {} message(s) across {} channel(s).".format(i_db.total_channel_messages(i_s), i_s.query(dernan_core.ChannelMessage.channel_name.distinct()).count()))
		click.echo("Commencing import...")
		query = i_s.query(dernan_core.ChannelMessage)
		with click.progressbar(query, query.count(), label="importing...", width=0) as op:
			for entry in op:
				cm_s.add(dernan_core.ChannelMessage(channel_name=entry.channel_name, channel_id=entry.channel_id, sender_name=entry.sender_name, sender_object=entry.sender_object, prefix=entry.prefix, message=entry.message, social=entry.social, verbatim=entry.verbatim, time=entry.time))
		click.echo("Import complete.")
		click.echo("Committing...")
		cm_s.commit()
		ending_total_messages = cm_db.total_channel_messages(cm_s)
		ending_total_channels = cm_s.query(dernan_core.ChannelMessage.channel_name.distinct()).count()
		try:
			total_growth_percent = round(float(ending_total_messages-starting_total_messages) / float(starting_total_messages) * 100, 2)
		except ZeroDivisionError:
			total_growth_percent = 100
		cm_s.close()
		i_s.close()
		click.echo("Done.")
		click.echo("The database has grown by {} entries and {} channel(s); {} percent".format(ending_total_messages-starting_total_messages, ending_total_channels-starting_total_channels, total_growth_percent))



if __name__ == '__main__':
	import_db()