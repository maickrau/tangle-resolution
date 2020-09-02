#!/usr/bin/python

import sys

graphfile = sys.argv[1]
anchorfile = sys.argv[2]
gaffile = sys.argv[3]
min_coverage = int(sys.argv[4])

def revcomp(s):
	comp = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
	return "".join(comp[c] for c in s[::-1])

def reversenode(node):
	return (">" if node[0] == "<" else "<") + node[1:]

def reversepath(path):
	return [reversenode(n) for n in path[::-1]]

def canon(path):
	fw = "".join(path)
	rev = "".join(reversepath(path))
	assert reversepath(reversepath(path)) == path
	if fw < rev: return (tuple(path), True)
	return (tuple(reversepath(path)), False)

def canonpair(n1, n2):
	fw = (n1, n2)
	rev = (reversenode(n2), reversenode(n1))
	if fw < rev: return fw
	return rev

def getseq(path):
	global node_seqs
	return "".join((node_seqs[n[1:]] if n[0] == ">" else revcomp(node_seqs[n[1:]])) for n in path)

node_seqs = {}

with open(graphfile) as f:
	for l in f:
		parts = l.strip().split('\t')
		if parts[0] == 'S':
			node_seqs[parts[1]] = parts[2]

anchors = set()
with open(anchorfile) as f:
	for l in f:
		anchors.add(l.strip())

alleles = {}
next_allele = 0
edge_coverage = {}
edge_overlap = {}
allele_name = {}
allele_coverage = {}
with open(gaffile) as f:
	for line in f:
		parts = line.strip().split('\t')
		path = []
		l = parts[5] + '>'
		last_break = 0
		for i in range(1, len(l)):
			if l[i] == '>' or l[i] == '<':
				path.append(l[last_break:i])
				last_break = i
		last_anchor = 0
		while last_anchor < len(path) and path[last_anchor][1:] not in anchors: last_anchor += 1
		if last_anchor == len(path): continue
		last_allele = None
		for i in range(last_anchor+1, len(path)):
			if path[i][1:] in anchors:
				(allele, direction) = canon(path[last_anchor:i+1])
				if allele not in alleles:
					alleles[allele] = next_allele
					allele_name[next_allele] = "".join(allele)
					allele_coverage[allele] = 0
					next_allele += 1
				allele_coverage[allele] += 1
				allelekey = (">" if direction else "<") + str(alleles[allele])
				last_anchor = i
				if last_allele is not None:
					key = canonpair(last_allele, allelekey)
					if key not in edge_coverage:
						edge_coverage[key] = 0
						assert key not in edge_overlap
						edge_overlap[key] = len(node_seqs[allele[0][1:]])
						if not direction: edge_overlap[key] = len(node_seqs[allele[-1][1:]])
					edge_coverage[key] += 1
					assert key in edge_overlap
				last_allele = allelekey

for allele in alleles:
	if allele_coverage[allele] < min_coverage: continue
	print("S\t" + allele_name[alleles[allele]] + "\t" + getseq(allele) + "\tFC:f:" + str(allele_coverage[allele] * len(getseq(allele))))
for edge in edge_coverage:
	if edge_coverage[edge] < min_coverage: continue
	print("L\t" + allele_name[int(edge[0][1:])] + "\t" + ("+" if edge[0][0] == ">" else "-") + "\t" + allele_name[int(edge[1][1:])] + "\t" + ("+" if edge[1][0] == ">" else "-") + "\t" + str(edge_overlap[edge]) + "M" + "\tec:i:" + str(edge_coverage[edge]))
