#!/usr/bin/python

import sys

k = int(sys.argv[1])

# graph from stdin
# graph to stdout

assert k % 2 == 1
remove_overlap = (k-1) / 2

node_seqs = {}
has_edge = set()
for l in sys.stdin:
	parts = l.strip().split('\t')
	if l[0] == 'S':
		node_seqs[parts[1]] = parts[2]
	if l[0] == 'L':
		print("L\t" + parts[1] + "\t" + parts[2] + "\t" + parts[3] + "\t" + parts[4] + "\t0M")
		has_edge.add((parts[1], parts[2] == "+"))
		has_edge.add((parts[3], parts[4] == "-"))

for node in node_seqs:
	seq = node_seqs[node]
	assert len(seq) > 2 * remove_overlap
	if (node, True) in has_edge:
		seq = seq[:-remove_overlap]
	if (node, False) in has_edge:
		seq = seq[remove_overlap:]
	print("S\t" + node + "\t" + seq)
