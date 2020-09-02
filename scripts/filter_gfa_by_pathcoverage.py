#!/usr/bin/python

import sys

min_coverage = int(sys.argv[1])
# gfa from stdin

def reverse(n):
	return n[:-1] + ("+" if n[-1] == "-" else "-")

def canon(n1, n2):
	fw = (n1, n2)
	bw = (reverse(n2), reverse(n1))
	if fw < bw: return fw
	return bw

nodes = []
edges = []
nodecoverage = {}
edgecoverage = {}

for l in sys.stdin:
	parts = l.strip().split('\t')
	if len(parts) < 2: continue
	if parts[0] == 'S':
		nodes.append((parts[1], l.strip()))
		nodecoverage[parts[1]] = set()
	if parts[0] == 'L':
		edges.append((canon(parts[1] + parts[2], parts[3] + parts[4]), l.strip()))
	if parts[0] == 'P':
		name = parts[1]
		path = parts[2].split(',')
		for n in path:
			nodecoverage[n[:-1]].add(name)
		for i in range(1, len(path)):
			old = path[i-1]
			new = path[i]
			key = canon(old, new)
			if key not in edgecoverage: edgecoverage[key] = set()
			edgecoverage[key].add(name)

max_tip_coverage = {}
for pair in edgecoverage:
	if pair[0] not in max_tip_coverage: max_tip_coverage[pair[0]] = 0
	if reverse(pair[1]) not in max_tip_coverage: max_tip_coverage[reverse(pair[1])] = 0
	max_tip_coverage[pair[0]] = max(max_tip_coverage[pair[0]], len(edgecoverage[pair]))
	max_tip_coverage[reverse(pair[1])] = max(max_tip_coverage[reverse(pair[1])], len(edgecoverage[pair]))

kept_tips = set()
for pair in edgecoverage:
	if max_tip_coverage[pair[0]] < min_coverage and max_tip_coverage[reverse(pair[1])] < min_coverage:
		kept_tips.add(pair[0])
		kept_tips.add(reverse(pair[1]))

for n in nodes:
	keep = True
	if len(nodecoverage[n[0]]) < min_coverage:
		keep = False
		# if str(n[0]) + "+" in kept_tips: keep = True
		# if str(n[0]) + "-" in kept_tips: keep = True
	if keep: print(n[1])

for e in edges:
	keep = True
	if e[0] in edgecoverage and len(edgecoverage[e[0]]) < min_coverage:
		keep = False
		# if e[0][0] in kept_tips and reverse(e[0][1]) in kept_tips: keep = True
	if keep: print(e[1])
