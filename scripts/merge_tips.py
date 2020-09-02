#!/usr/bin/python

import sys

graphfile = sys.argv[1]
# tips from stdin

nodelens = {}

def format(n):
	return (">" if n[1] else "<") + n[0]

def canon(n1, n2, n3, n4):
	global nodelens
	fw = (n1, n2, n3, n4)
	bw = ((n2[0], not n2[1]), (n1[0], not n1[1]), nodelens[n2[0]] - n4 - 1, nodelens[n1[0]] - n3 - 1)
	if fw < bw: return fw
	return bw

with open(graphfile) as f:
	for l in f:
		if l[0] == 'S':
			parts = l.strip().split('\t')
			nodelens[parts[1]] = len(parts[2])

collected = {}

for l in sys.stdin:
	parts = l.strip().split('\t')
	if len(parts) == 0: continue
	fromnode = (parts[0][1:], parts[0][0] == '>')
	tonode = (parts[2][1:], parts[2][0] == '>')
	key = canon(fromnode, tonode, int(parts[1]), int(parts[3]))
	if key not in collected: collected[key] = []
	seq = str(int(parts[6]) - int(parts[5]))
	if len(parts) == 8: seq = parts[7]
	collected[key].append((parts[4], int(parts[6]) - int(parts[5]), seq))

for key in collected:
	print(format(key[0]) + "\t" + str(key[2]) + "\t" + format(key[1]) + "\t" + str(key[3]) + "\t" + str(len(collected[key])) + "\t" + ",".join(c[2] for c in collected[key]))

