#!/usr/bin/python

import fileinput

def reverse(n):
	return (n[0], not n[1])

def format(n):
	return ('>' if n[1] else '<') + n[0]

connections = {}

lines = list(fileinput.input())

for l in lines:
	lst = l.strip() + '<'
	last_break = 0
	parts = []
	for i in range(1, len(lst)):
		if lst[i] == '<' or lst[i] == '>':
			parts.append(lst[last_break:i])
			last_break = i
	fromnode = (parts[0][1:], parts[0][0] == '>')
	tonode = (parts[-1][1:], parts[-1][0] == '>')
	if fromnode not in connections: connections[fromnode] = set()
	if tonode not in connections: connections[tonode] = set()
	if reverse(fromnode) not in connections: connections[reverse(fromnode)] = set()
	if reverse(tonode) not in connections: connections[reverse(tonode)] = set()
	connections[fromnode].add(reverse(tonode))
	connections[reverse(tonode)].add(fromnode)

fine_edges = set()
too_many_edges = set()

fine_nodes = set()
partially_fine_nodes = set()
too_many_nodes = set()
missing_nodes = set()

for pos in connections:
	if len(connections[pos]) == 1 or len(connections[reverse(pos)]) == 1:
		partially_fine_nodes.add(pos[0])
	if len(connections[pos]) == 1 and len(connections[reverse(pos)]) == 1:
		fine_nodes.add(pos[0])
		continue
	if len(connections[pos]) == 0:
		missing_nodes.add(format(pos))
	if len(connections[pos]) >= 2:
		too_many_nodes.add(format(pos))

for node in fine_nodes:
	partially_fine_nodes.remove(node)

for l in lines:
	lst = l.strip() + '<'
	last_break = 0
	parts = []
	for i in range(1, len(lst)):
		if lst[i] == '<' or lst[i] == '>':
			parts.append(lst[last_break:i])
			last_break = i
	fromnode = (parts[0][1:], parts[0][0] == '>')
	tonode = (parts[-1][1:], parts[-1][0] == '>')
	if len(connections[fromnode]) == 1 and len(connections[reverse(tonode)]) == 1:
		fine_edges.add(l.strip())
	else:
		assert len(connections[fromnode]) >= 1
		assert len(connections[reverse(tonode)]) >= 1
		assert len(connections[fromnode]) >= 2 or len(connections[reverse(tonode)]) >= 2
		too_many_edges.add(l.strip())

print("Nodes missing connection: " + str(len(missing_nodes)))
for node in missing_nodes:
	print(node)

print("Nodes with extra connections: " + str(len(too_many_nodes)))
for node in too_many_nodes:
	print(node)

print("Inconsistent edges: " + str(len(too_many_edges)))
for edge in too_many_edges:
	print(edge)

print("Partially fine nodes: " + str(len(partially_fine_nodes)))
for node in partially_fine_nodes:
	print(node)

print("Fine nodes: " + str(len(fine_nodes)))
for node in fine_nodes:
	print(node)

print("Fine edges: " + str(len(fine_edges)))
for edge in fine_edges:
	print(edge)
