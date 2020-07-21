#!/usr/bin/python

import sys

paffile = sys.argv[1]
contigfile = sys.argv[2]
# input graph from stdin

node_seqs = {}
edges = []
for l in sys.stdin:
	parts = l.strip().split('\t')
	if parts[0] == 'S':
		node_seqs[parts[1]] = parts[2]
	if parts[0] == 'L':
		edges.append((parts[1], parts[2], parts[3], parts[4], int(parts[5][:-1])))

with open(contigfile, 'w') as f:
	for node in node_seqs:
		f.write('>' + node + '\n')
		f.write(node_seqs[node] + '\n')

with open(paffile, 'w') as f:
	for edge in edges:
		fw = edge[1] == edge[3]
		line = edge[0] + "\t" + str(len(node_seqs[edge[0]])) + "\t"
		if edge[1] == '+':
			line += str(len(node_seqs[edge[0]]) - edge[4])
			line += '\t'
			line += str(len(node_seqs[edge[0]]))
		else:
			line += '0'
			line += '\t'
			line += str(edge[4])
		line += '\t'
		line += '+' if fw else '-'
		line += '\t'
		line += edge[2] + "\t" + str(len(node_seqs[edge[2]])) + "\t"
		if edge[3] == '+':
			line += '0'
			line += '\t'
			line += str(edge[4])
		else:
			line += str(len(node_seqs[edge[2]]) - edge[4])
			line += '\t'
			line += str(len(node_seqs[edge[2]]))
		line += '\t'
		line += str(edge[4])
		line += "\t0\t100\tcg:Z:" + str(edge[4]) + "M"
		f.write(line + "\n")

