#!/usr/bin/python

import sys

graph_file = sys.argv[1]
start_node = sys.argv[2]

def revcomp(s):
	comp = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'a': 'T', 't': 'A', 'c': 'G', 'g': 'C'}
	return "".join(comp[c] for c in s[::-1])

node_seq = {}
outneighbor = {}

with open(graph_file) as f:
	for l in f:
		parts = l.strip().split('\t')
		if parts[0] == 'S':
			node_seq[parts[1]] = parts[2]
		if parts[0] == 'L':
			outneighbor[('>' if parts[2] == '+' else '<') + parts[1]] = ('>' if parts[4] == '+' else '<') + parts[3]
			outneighbor[('<' if parts[4] == '+' else '>') + parts[3]] = ('<' if parts[2] == '+' else '>') + parts[1]

path_name = ""
path_seq = ""
while True:
	path_name += start_node
	add = node_seq[start_node[1:]]
	if start_node[0] == '<': add = revcomp(add)
	path_seq += add
	if start_node not in outneighbor: break
	start_node = outneighbor[start_node]

print(">path_" + path_name.strip())
print(path_seq.strip())
