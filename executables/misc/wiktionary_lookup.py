#!/usr/bin/env python
# Simple script that just uses a neat library to fetch various things about a word or phrase wiktionary knows about.

import json
import sys
from wiktionaryparser import WiktionaryParser

# Functions? Who needs em. Not this fire and forget code, that's who. That's not who, that is. Who not? Not who? Not you.

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("Usage: wiktionary_lookup.py word-or-phrase[word-or-phrase]")
		sys.exit(1)
	parser = WiktionaryParser()
	results = []
	for item in sys.argv[1:]:
		data = parser.fetch(item)
		results.append(data)
	resultstr = json.dumps(results)
	print(resultstr)
