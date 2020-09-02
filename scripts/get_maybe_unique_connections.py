#!/usr/bin/python

import sys

unique_nodes_file = sys.argv[1]
# paths from stdin

def parse_path(s):
	l = s.strip()+'>'
	last_break = 0
	path = []
	for i in range(1, len(l)):
		if l[i] == '<' or l[i] == '>':
			path.append((l[last_break+1:i], l[last_break] == '>'))
			last_break = i
	return path

def canon(n1, n2):
	if n1 < n2: return (n1, n2)
	return ((n2[0], not n2[1]), (n1[0], not n1[1]))

unique_nodes = set()

with open(unique_nodes_file) as f:
	for l in f:
		unique_nodes.add(l.strip())

edges = {}

for line in sys.stdin:
	path = parse_path(line)
	last_unique = None
	for n in path:
		if n[0] not in unique_nodes: continue
		if last_unique is None:
			last_unique = n
			continue
		edge = canon(last_unique, n)
		if edge not in edges: edges[edge] = 0
		edges[edge] += 1
		last_unique = n

for n in unique_nodes:
	print("S\t" + str(n) + "\t*")

for e in edges:
	print("L\t" + e[0][0] + "\t" + ("+" if e[0][1] else "-") + "\t" + e[1][0] + "\t" + ("+" if e[1][1] else "-") + "\t0M\trc:Z:" + str(edges[e]))
