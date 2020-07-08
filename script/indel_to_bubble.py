#!/usr/bin/python

import fileinput
import sys

nodeseqs = {}
max_node = 0
edges = {}

def reverse(n):
	return (n[0], '+' if n[1] == '-' else '-')

for l in fileinput.input():
	parts = l.strip().split('\t')
	if l[0] == 'S':
		nodeseqs[parts[1]] = parts[2]
		max_node = max(max_node, int(parts[1]))
	if l[0] == 'L':
		from_node = (parts[1], parts[2])
		to_node = (parts[3], parts[4])
		if from_node not in edges: edges[from_node] = set()
		if reverse(to_node) not in edges: edges[reverse(to_node)] = set()
		edges[from_node].add(to_node)
		edges[reverse(to_node)].add(reverse(from_node))

max_node += 1
added_bubbles = 0

nodes = list(nodeseqs)

for n in nodes:
	if (n, '+') not in edges or len(edges[(n, '+')]) != 1: continue
	if (n, '-') not in edges or len(edges[(n, '-')]) != 1: continue
	front_neighbor = reverse(list(edges[(n, '+')])[0])
	back_neighbor = reverse(list(edges[(n, '-')])[0])
	assert front_neighbor in edges
	assert back_neighbor in edges
	if len(edges[front_neighbor]) != 2: continue
	if len(edges[back_neighbor]) != 2: continue
	front_neighbor_edges = edges[front_neighbor]
	back_neighbor_edges = edges[back_neighbor]
	valid = True
	for edge in front_neighbor_edges:
		if edge != (n, '-') and edge != reverse(back_neighbor):
			valid = False
			break
	for edge in back_neighbor_edges:
		if edge != (n, '+') and edge != reverse(front_neighbor):
			valid = False
			break
	if not valid: continue
	if len(nodeseqs[front_neighbor[0]]) == 1:
		sys.stderr.write("Cannot bubblify " + str(n) + "\n")
		continue
	assert len(nodeseqs[front_neighbor[0]]) >= 2
	new_node_seq = ""
	new_node_id = str(max_node)
	max_node += 1
	if front_neighbor[1] == '+':
		comp = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
		new_node_seq = comp[nodeseqs[front_neighbor[0]][-1]]
		nodeseqs[front_neighbor[0]] = nodeseqs[front_neighbor[0]][:-1]
	else:
		new_node_seq = nodeseqs[front_neighbor[0]][0]
		nodeseqs[front_neighbor[0]] = nodeseqs[front_neighbor[0]][1:]
	nodeseqs[new_node_id] = new_node_seq
	nodeseqs[n] += new_node_seq
	edges[front_neighbor] = set([(n, '-'), (new_node_id, '-')])
	edges[back_neighbor] = set([(n, '+'), (new_node_id, '+')])
	edges[(new_node_id, '+')] = set([reverse(front_neighbor)])
	edges[(new_node_id, '-')] = set([reverse(back_neighbor)])
	added_bubbles += 1
	# sys.stderr.write(str(new_node_id) + ':(' + str(back_neighbor) + "-" + str(n) + "-" + str(front_neighbor) + ") ")

# sys.stderr.write('\n')

for n in nodeseqs:
	print('S\t' + str(n) + '\t' + nodeseqs[n])

for edge in edges:
	for target in edges[edge]:
		print('L\t' + edge[0] + '\t' + edge[1] + '\t' + target[0] + '\t' + target[1] + '\t0M')


