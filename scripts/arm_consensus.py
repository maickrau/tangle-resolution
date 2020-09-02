#!/usr/bin/python

import sys

graphfile = sys.argv[1]
corenodefile = sys.argv[2]
gaffile = sys.argv[3]
startnode = sys.argv[4]

def revcomp(s):
	comp = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
	return "".join(comp[c] for c in s[::-1])

def getseq(n):
	global nodeseqs
	if n[0] == '>': return nodeseqs[n[1:]]
	return revcomp(nodeseqs[n[1:]])

def reversenode(n):
	return (">" if n[0] == "<" else "<") + n[1:]

def reversepath(p):
	return [reversenode(n) for n in p[::-1]]

nodeseqs = {}
with open(graphfile) as f:
	for l in f:
		if l[0] == 'S':
			parts = l.strip().split('\t')
			nodeseqs[parts[1]] = parts[2]

core_nodes = set()
with open(corenodefile) as f:
	for l in f:
		core_nodes.add(l.strip())

alns_from_start = []
with open(gaffile) as f:
	for l in f:
		path = []
		parts = l.strip().split('\t')
		pathstr = parts[5] + '>'
		last_break = 0
		for i in range(1, len(pathstr)):
			if pathstr[i] == '<' or pathstr[i] == '>':
				path.append(pathstr[last_break:i])
				last_break = i
		for i in range(0, len(path)):
			if path[i][1:] == startnode[1:]:
				if path[i][0] == startnode[0]:
					alns_from_start.append(path[i:])
					break
				else:
					alns_from_start.append(reversepath(path[:i+1]))

current_index = []
for i in range(0, len(alns_from_start)):
	current_index.append(1)

bubble_num = 0
last_bubble_end = startnode + "_0_0_core"
print("S\t" + last_bubble_end + "\t" + getseq(startnode) + "\tFC:i:" + str(len(alns_from_start) * len(getseq(startnode))))
while True:
	bubble_node_num = 0
	next_end = None
	# alleles does NOT contain start or end nodes
	# only middle nodes
	alleles = {}
	total_coverage = 0
	for i in range(0, len(alns_from_start)):
		start_index = current_index[i]
		while current_index[i] < len(alns_from_start[i]) and alns_from_start[i][current_index[i]][1:] not in core_nodes:
			current_index[i] += 1
		if current_index[i] == len(alns_from_start[i]):
			continue
		assert next_end is None or alns_from_start[i][current_index[i]] == next_end
		next_end = alns_from_start[i][current_index[i]]
		key = tuple(alns_from_start[i][start_index:current_index[i]])
		current_index[i] += 1
		if key not in alleles: alleles[key] = 0
		alleles[key] += 1
		total_coverage += 1
	if len(alleles) == 0: break
	bubble_end_name = next_end + "_" + str(bubble_num) + "_" + str(bubble_node_num) + "_core"
	bubble_node_num += 1
	print("S\t" + bubble_end_name + "\t" + getseq(next_end) + "\tFC:i:" + str(total_coverage * len(getseq(next_end))))
	for allele in alleles:
		last_node = last_bubble_end
		for n in allele:
			node_name = n + "_" + str(bubble_num) + "_" + str(bubble_node_num) + "_allele"
			bubble_node_num += 1
			print("S\t" + node_name + "\t" + getseq(n) + "\tFC:i:" + str(alleles[allele] * len(getseq(n))))
			print("L\t" + last_node + "\t+\t" + node_name + "\t+\t0M")
			last_node = node_name
		print("L\t" + last_node + "\t+\t" + bubble_end_name + "\t+\t0M")
	bubble_num += 1
	last_bubble_end = bubble_end_name
