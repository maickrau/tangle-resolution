#!/usr/bin/python

import sys

start_node = sys.argv[1]
# graph from stdin

def find(n, parent):
	while parent[n] != parent[parent[n]]:
		parent[n] = parent[parent[n]]
	return parent[n]

def union(n1, n2, parent, rank):
	p1 = find(n1, parent)
	p2 = find(n2, parent)
	if rank[p1] < rank[p2]: (p1, p2) = (p2, p1)
	parent[p2] = p1
	if rank[p1] == rank[p2]: rank[p1] += 1

lines = []

parent = {}
rank = {}

for l in sys.stdin:
	parts = l.strip().split('\t')
	if l[0] == 'S':
		lines.append((parts[1], l.strip()))
		assert parts[1] not in parent
		assert parts[1] not in rank
		parent[parts[1]] = parts[1]
		rank[parts[1]] = 1
	if l[0] == 'L':
		lines.append((parts[1], l.strip()))
		union(parts[1], parts[3], parent, rank)

for l in lines:
	if find(l[0], parent) == find(start_node, parent):
		print(l[1])
