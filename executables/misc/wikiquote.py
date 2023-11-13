#!/usr/bin/env python
# Script that wraps the wikiquotes package, which itself parses wikiquotes.
# Accept arguments, output json.

import json, os, sys
import wikiquotes

ops = ["search", "random_quote", "quote_of_the_day"]

if __name__ == '__main__':
	if len(sys.argv) < 2 or (len(sys.argv) == 2 and not sys.argv[1] == "quote_of_the_day"):
		print(("Usage: {} {} <author for search and random quote>".format(sys.argv[0], " | ".join(ops))))
		sys.exit(1)
	elif not sys.argv[1] in ops:
		print(("Unknown argument. Must be one of: ", ", ".join(ops)))
		sys.exit(1)
	
	lang = os.environ.get("WIKIQUOTE_LANGUAGE", "english")
	if (sys.argv[1] == "quote_of_the_day") == False:
		term = sys.argv[2]
	if sys.argv[1] == "search":
		# Search wikiquotes
		results = wikiquotes.search(term, lang)
		res_str = json.dumps(results)
	elif sys.argv[1] == "random_quote":
		results = wikiquotes.random_quote(term, lang)
	elif sys.argv[1] == "quote_of_the_day":
		results = wikiquotes.quote_of_the_day(lang)
	res_str = json.dumps(results)
	print(res_str)
