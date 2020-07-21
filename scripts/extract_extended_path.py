#!/usr/bin/python

import sys

graphfile = sys.argv[1]
# gaf from stdin

def revcomp(s):
	comp = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'a': 'T', 't': 'A', 'c': 'G', 'g': 'C'}
	return "".join(comp[c] for c in s[::-1])

nodeseqs = {}

with open(graphfile) as f:
	for l in f:
		if l[0] == 'S':
			parts = l.strip().split('\t')
			nodeseqs[parts[1]] = parts[2]
		if l[0] == 'L':
			parts = l.strip().split('\t')
			if parts[5] != "0M":
				print("Graphs with overlap are not supported")
				sys.stderr.write("Graphs with overlap are not supported\n")
				sys.exit(1)

for l in sys.stdin:
	parts = l.strip().split('\t')
	if len(parts) < 11: continue
	readname = parts[0]
	if parts[2] != "0" or parts[3] != parts[1]:
		# no partial alignments
		continue
	if float(parts[9]) / float(parts[10]) < 0.98:
		# no identity less than 98%
		continue
	seq = ""
	last_break = 0
	parts[5] += '>'
	for i in range(1, len(parts[5])):
		if parts[5][i] == '>' or parts[5][i] == '<':
			node = parts[5][last_break+1:i]
			fw = parts[5][last_break] == '>'
			add_seq = nodeseqs[node]
			if not fw: add_seq = revcomp(add_seq)
			seq += add_seq
			last_break = i
	print(">" + readname)
	print(seq)

