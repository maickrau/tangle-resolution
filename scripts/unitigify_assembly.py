#!/usr/bin/python

import sys
from Gfa import *

infile = sys.argv[1]
outfile = sys.argv[2]
mappingfile = sys.argv[3]

def revcomp(s):
	rev = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'a': 't', 't': 'a', 'c': 'g',  'g': 'c'}
	return ''.join(rev[c] for c in s[::-1])

graph = Graph()
graph.load(infile)
graph.remove_nonexistent_edges()

unitig_tips = set() # pointing outwards
unitig_mapping = {}
result = Graph()
next_unitig = 1

def getset(s):
	assert(len(s) == 1)
	for item in s:
		return item

def get_unitig(pos):
	global unitig_mapping
	global result
	global next_unitig
	global graph
	global unitig_tips
	assert pos[0] not in unitig_mapping
	unitig_tips.add(reverse(pos))
	unitig_mapping[pos[0]] = (next_unitig, pos[1])
	unitig = Node()
	unitig.nodeid = next_unitig
	unitig.nodeseq = graph.nodes[pos[0]].nodeseq
	if not pos[1]: unitig.nodeseq = revcomp(unitig.nodeseq)
	while len(graph.edges[pos]) == 1 and getset(graph.edges[pos])[0][0] != pos[0]:
		nextpos = getset(graph.edges[pos])[0]
		revnextpos = reverse(nextpos)
		overlap = getset(graph.edges[pos])[1][0]
		if len(graph.edges[revnextpos]) != 1: break
		pos = nextpos
		assert pos[0] not in unitig_mapping
		unitig_mapping[pos[0]] = (next_unitig, pos[1])
		add = graph.nodes[pos[0]].nodeseq
		if not pos[1]: add = revcomp(add)
		add = add[overlap:]
		unitig.nodeseq += add
	unitig_tips.add(pos)
	result.nodes[next_unitig] = unitig
	next_unitig += 1

def get_circular_unitig(pos):
	global unitig_mapping
	global result
	global next_unitig
	global graph
	global unitig_mapping
	assert pos[0] not in unitig_mapping
	start = pos
	unitig_tips.add(start)
	assert len(graph.edges[start]) == 1
	pos = getset(graph.edges[start])[0]
	unitig_tips.add(reverse(pos))
	assert pos[0] not in unitig_mapping
	unitig_mapping[pos[0]] = (next_unitig, pos[1])
	unitig = Node()
	unitig.nodeid = next_unitig
	unitig.nodeseq = graph.nodes[pos[0]].nodeseq
	if not pos[1]: unitig.nodeseq = revcomp(unitig.nodeseq)
	while pos != start:
		assert len(graph.edges[pos]) == 1
		nextpos = getset(graph.edges[pos])[0]
		revnextpos = reverse(nextpos)
		overlap = getset(graph.edges[pos])[1][0]
		assert len(graph.edges[revnextpos]) == 1
		assert nextpos[0] != pos[0]
		pos = nextpos
		assert pos[0] not in unitig_mapping
		unitig_mapping[pos[0]] = (next_unitig, pos[1])
		add = graph.nodes[pos[0]].nodeseq
		if not pos[1]: add = revcomp(add)
		add = add[overlap:]
		unitig.nodeseq += add
	result.nodes[next_unitig] = unitig
	next_unitig += 1

for node in graph.nodes:
	n = graph.nodes[node]
	fwpos = (n.nodeid, True)
	bwpos = (n.nodeid, False)
	if len(graph.edges[bwpos]) != 1 or getset(graph.edges[bwpos])[0][0] == n.nodeid:
		if n.nodeid not in unitig_mapping: get_unitig(fwpos)
		for target in graph.edges[bwpos]:
			if target[0][0] in unitig_mapping: continue
			get_unitig(target[0])
	if len(graph.edges[fwpos]) != 1 or getset(graph.edges[fwpos])[0][0] == n.nodeid:
		if n.nodeid not in unitig_mapping: get_unitig(bwpos)
		for target in graph.edges[fwpos]:
			if target[0][0] in unitig_mapping: continue
			get_unitig(target[0])

for node in graph.nodes:
	n = graph.nodes[node]
	if n.nodeid in unitig_mapping: continue
	fwpos = (n.nodeid, True)
	bwpos = (n.nodeid, False)
	assert len(graph.edges[fwpos]) == 1
	assert len(graph.edges[bwpos]) == 1
	if (next_unitig, True) not in result.edges: result.edges[(next_unitig, True)] = set()
	result.edges[(next_unitig, True)].add(((next_unitig, True), getset(graph.edges[fwpos])[1]))
	get_circular_unitig(fwpos)

for node in graph.nodes:
	n = graph.nodes[node]
	assert n.nodeid in unitig_mapping
	result.nodes[unitig_mapping[n.nodeid][0]].length += n.length
	result.nodes[unitig_mapping[n.nodeid][0]].readcount += n.readcount

mapping_edges = []

for edge in graph.edges:
	assert edge[0] in unitig_mapping
	if edge not in unitig_tips: continue
	frompos = unitig_mapping[edge[0]]
	if not edge[1]: frompos = reverse(frompos)
	for target in graph.edges[edge]:
		if reverse(target[0]) not in unitig_tips: continue
		assert target[0][0] in unitig_mapping
		topos = unitig_mapping[target[0][0]]
		if not target[0][1]: topos = reverse(topos)
		if frompos not in result.edges: result.edges[frompos] = set()
		result.edges[frompos].add((topos, target[1]))
		mapping_edges.append((edge, target[0]))

result.write(outfile)

with open(mappingfile, 'w') as f:
	for n in unitig_mapping:
		f.write('N\t' + str(n) + '\t' + str(unitig_mapping[n][0]) + '\t' + ("+" if unitig_mapping[n][1] else "-") + '\n')
	for e in mapping_edges:
		f.write('E\t' + str(e[0][0]) + '\t' + ("+" if e[0][1] else "-") + '\t' + str(e[1][0]) + '\t' + ("+" if e[1][1] else "-") + '\n')
		f.write('E\t' + str(e[1][0]) + '\t' + ("+" if not e[1][1] else "-") + '\t' + str(e[0][0]) + '\t' + ("+" if not e[0][1] else "-") + '\n')
