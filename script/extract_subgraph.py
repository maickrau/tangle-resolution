#!/usr/bin/python

import sys

valid_nodes_file = sys.argv[1]
# graph from stdin

valid_nodes = set()

with open(valid_nodes_file) as f:
	for l in f:
		valid_nodes.add(l.strip())

for l in sys.stdin:
	parts = l.strip().split('\t')
	if parts[0] == 'S' and parts[1] not in valid_nodes: continue
	if parts[0] == 'L' and (parts[1] not in valid_nodes or parts[3] not in valid_nodes): continue
	print(l.strip())
