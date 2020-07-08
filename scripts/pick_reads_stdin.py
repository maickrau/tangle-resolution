#!/usr/bin/python

import sys
import fileinput

readnamefile = "picked.txt"

readnames = set()

with open(readnamefile) as f:
	for l in f:
		readnames.add(l.strip().split('\t')[0])

printing = False

for l in fileinput.input():
    if l[0] == '>':
        name = l.strip()[1:].split(" ")[0]
        valid_name = name in readnames
        printing = valid_name
    if printing:
	print(l.strip())
