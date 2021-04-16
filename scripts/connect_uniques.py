#!/usr/bin/python

import sys

graph_file = sys.argv[1]
forbidden_ends_file = sys.argv[2]
resolving_paths_file = sys.argv[3]
# graph to stdout

def revnode(n):
	assert len(n) >= 2
	assert n[0] == '>' or n[0] == '<'
	return (">" if n[0] == "<" else "<") + n[1:]

def canontip(left, right):
	fwstr = left + right
	bwstr = right + left
	if bwstr < fwstr: return (right, left)
	return (left, right)

resolvable_ends = set()
path_covered_nodes = set()
paths = []

with open(resolving_paths_file) as f:
	for line in f:
		l = line.strip() + '>'
		last_break = 0
		path = []
		for i in range(1, len(l)):
			if l[i] == '<' or l[i] == '>':
				path.append(l[last_break:i])
				last_break = i
		if len(path) == 0: continue
		resolvable_ends.add(path[0])
		resolvable_ends.add(revnode(path[-1]))
		paths.append(path)

with open(forbidden_ends_file) as f:
	for l in f:
		parts = l.strip().split(',')
		for part in parts:
			if part in resolvable_ends: resolvable_ends.remove(part)

for path in paths:
	if path[0] not in resolvable_ends or revnode(path[-1]) not in resolvable_ends: continue
	for node in path[1:-1]:
		path_covered_nodes.add(node[1:])

sys.stderr.write(str(len(resolvable_ends)) + " resolvable ends\n")
sys.stderr.write(str(resolvable_ends) + "\n")
sys.stderr.write(str(len(path_covered_nodes)) + " path covered nodes\n")

node_seq = {}
base_overlaps = {}

with open(graph_file) as f:
	for l in f:
		parts = l.strip().split('\t')
		if parts[0] == 'S':
			node_seq[parts[1]] = parts[2]
			if parts[1] in path_covered_nodes: continue
		elif parts[0] == 'L':
			check_from = (">" if parts[2] == "+" else "<") + parts[1]
			check_to = ("<" if parts[4] == "+" else ">") + parts[3]
			base_from = check_from.split('_')[0]
			base_to = check_to.split('_')[0]
			key = canontip(base_from, base_to)
			base_overlaps[key] = parts[5]
			if check_from in resolvable_ends or check_to in resolvable_ends:
				continue
			if parts[1] in path_covered_nodes or parts[3] in path_covered_nodes: continue
		print(l.strip())

# sys.stderr.write(str(len(node_seq)) + " nodes\n")

num_insertions = {}

with open(resolving_paths_file) as f:
	for line in f:
		l = line.strip() + '>'
		last_break = 0
		path = []
		for i in range(1, len(l)):
			if l[i] == '<' or l[i] == '>':
				path.append(l[last_break:i])
				last_break = i
		sys.stderr.write("path " + str(path) + "\n")
		assert len(path) >= 2
		if len(path) == 0: continue
		if path[0] not in resolvable_ends or ((">" if path[-1][0] == "<" else "<") + path[-1][1:]) not in resolvable_ends: continue
		sys.stderr.write("insert path " + str(path) + "\n")
		last_node = path[0]
		for i in range(1, len(path)-1):
			if path[i][1:] not in num_insertions: num_insertions[path[i][1:]] = 0
			num_insertions[path[i][1:]] += 1
			this_node = path[i][0] + path[i][1:] + "_" + str(num_insertions[path[i][1:]])
			print("S\t" + this_node[1:] + "\t" + node_seq[path[i][1:]])
			overlap = "0M"
			key = canontip(path[i-1], revnode(path[i]))
			assert key in base_overlaps
			overlap = base_overlaps[key]
			print("L\t" + last_node[1:] + "\t" + ("+" if last_node[0] == ">" else "-") + "\t" + this_node[1:] + "\t" + ("+" if this_node[0] == ">" else "-") + "\t" + overlap)
			last_node = this_node
		key = canontip(path[-2], revnode(path[-1]))
		assert key in base_overlaps
		overlap = base_overlaps[key]
		print("L\t" + last_node[1:] + "\t" + ("+" if last_node[0] == ">" else "-") + "\t" + path[-1][1:] + "\t" + ("+" if path[-1][0] == ">" else "-") + "\t" + overlap)
