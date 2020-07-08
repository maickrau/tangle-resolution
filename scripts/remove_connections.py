#!/usr/bin/python

import sys

forbid_from = sys.argv[1]
forbid_to = sys.argv[2]

forbid_from_reverse = ('>' if forbid_from[0] == '<' else '<') + forbid_from[1:]
forbid_to_reverse = ('>' if forbid_to[0] == '<' else '<') + forbid_to[1:]

forbade = 0

for line in sys.stdin:
	l = line.strip()
	if l.find(forbid_from) != -1 and l.find(forbid_to) != -1:
		if l.find(forbid_to) > l.find(forbid_from):
			forbade += 1
			continue
	if l.find(forbid_to_reverse) != -1 and l.find(forbid_from_reverse) != -1:
		if l.find(forbid_from_reverse) > l.find(forbid_to_reverse):
			forbade += 1
			continue
	print(l.strip())

sys.stderr.write("forbade " + str(forbade) + " connections " + forbid_from + " " + forbid_to + "\n")