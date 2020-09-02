#!/usr/bin/python

import sys

longnodefile = sys.argv[1]
pathfile = sys.argv[2]

longnodes = set()
with open(longnodefile) as f:
	for l in f:
		longnodes.add(l.strip())

with open(pathfile) as f:
	for line in f:
		l = line.strip() + '>'
		path = ""
		last_break = 0
		for i in range(1, len(l)):
			if l[i] == '>' or l[i] == '<':
				if l[last_break+1:i] in longnodes:
					path += l[last_break:i]
				last_break = i
		print(path)