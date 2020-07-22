#!/usr/bin/python

import sys

# graphs from argv[1:]
# contigs to stdout

def revcomp(s):
	comp = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'a': 'T', 't': 'A', 'c': 'G', 'g': 'C'}
	return "".join(comp[c] for c in s[::-1])

def getone(s):
	for n in s:
		return n

next_id = 1

for filename in sys.argv[1:]:
	edges = {}
	nodeseqs = {}
	with open(filename) as f:
		for l in f:
			if l[0] == 'S':
				parts = l.strip().split('\t')
				nodeseqs[parts[1]] = parts[2]
				if (parts[1], True) not in edges: edges[(parts[1], True)] = set()
				if (parts[1], False) not in edges: edges[(parts[1], False)] = set()
			if l[0] == 'L':
				parts = l.strip().split('\t')
				overlap = int(parts[5][:-1])
				edges[(parts[1], True if parts[2] == "+" else False)].add(((parts[3], True if parts[4] == "+" else False), overlap))
				edges[(parts[3], True if parts[4] == "-" else False)].add(((parts[1], True if parts[2] == "-" else False), overlap))
	for n in nodeseqs:
		contig = nodeseqs[n]
		pos = (n, True)
		while len(edges[pos]) == 1:
			(pos, overlap) = getone(edges[pos])
			add = nodeseqs[pos[0]]
			if not pos[1]: add = revcomp(add)
			add = add[overlap:]
			contig += add
		bw = ""
		pos = (n, False)
		while len(edges[pos]) == 1:
			(pos, overlap) = getone(edges[pos])
			add = nodeseqs[pos[0]]
			if not pos[1]: add = revcomp(add)
			add = add[overlap:]
			bw += add
		contig = revcomp(bw) + contig
		print(">" + str(next_id))
		print(contig)
		next_id += 1
