#!/usr/bin/python

import sys

uniquefile = sys.argv[1]
graphfile = sys.argv[2]
connectionfile = sys.argv[3]

def find(s, parent):
	while parent[s] != parent[parent[s]]:
		parent[s] = parent[parent[s]]
	return parent[s]

def union(s1, s2, parent, rank):
	p1 = find(s1, parent)
	p2 = find(s2, parent)
	if rank[p1] < rank[p2]: (p1, p2) = (p2, p1)
	parent[p2] = p1
	if rank[p2] == rank[p1]: rank[p1] += 1

def reverse(n):
	return (">" if n[0] == '<' else '<') + n[1:]

unique_nodes = set()

with open(uniquefile) as f:
	for l in f:
		unique_nodes.add(l.strip())

parent = {}
rank = {}

with open(graphfile) as f:
	for l in f:
		if l[0] == 'S':
			parts = l.strip().split('\t')
			parent[">" + parts[1]] = ">" + parts[1]
			parent["<" + parts[1]] = "<" + parts[1]
			rank[">" + parts[1]] = 1
			rank["<" + parts[1]] = 1
			if parts[1] not in unique_nodes:
				union(">" + parts[1], "<" + parts[1], parent, rank)
		if l[0] == 'L':
			parts = l.strip().split('\t')
			fromend = (">" if parts[2] == '+' else '<') + parts[1]
			toend = ("<" if parts[4] == '+' else '>') + parts[3]
			union(fromend, toend, parent, rank)

has_connection = set()

with open(connectionfile) as f:
	for line in f:
		l = line.strip() + ">"
		last_break = 0
		path = []
		for i in range(1, len(l)):
			if l[i] == '<' or l[i] == '>':
				path.append(l[last_break:i])
				last_break = i
		assert len(path) >= 2
		fwkey = path[0]
		bwkey = reverse(path[-1])
		has_connection.add(fwkey)
		has_connection.add(bwkey)

forbidden_tangles = set()

for node in unique_nodes:
	if ">" + node not in has_connection:
		forbidden_tangles.add(find(">" + node, parent))
	if "<" + node not in has_connection:
		forbidden_tangles.add(find("<" + node, parent))

for node in unique_nodes:
	if find(">" + node, parent) in forbidden_tangles:
		print(">" + node)
	if find("<" + node, parent) in forbidden_tangles:
		print("<" + node)
