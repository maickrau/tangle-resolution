#!/usr/bin/python

import sys

# graph from stdin
# edge-contigs to stdout

def revcomp(s):
	comp = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
	return "".join(comp[c] for c in s[::-1])

nodeseqs = {}
edges = []
for l in sys.stdin:
	parts = l.strip().split('\t')
	if l[0] == 'S':
		nodeseqs[parts[1]] = parts[2]
	if l[0] == 'L':
		edges.append((parts[1], parts[2] == "+", parts[3], parts[4] == "+", int(parts[5][:-1])))

next_contig = 0
for edge in edges:
	print(">" + str(next_contig))
	next_contig += 1
	seq = nodeseqs[edge[0]]
	if not edge[1]: seq = revcomp(seq)
	add = nodeseqs[edge[2]]
	if not edge[3]: add = revcomp(add)
	print(seq + add[edge[4]:])
