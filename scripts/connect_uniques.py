#!/usr/bin/python

import sys

graph_file = sys.argv[1]
forbidden_ends_file = sys.argv[2]
resolving_paths_file = sys.argv[3]

resolvable_ends = set()

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
		resolvable_ends.add(('>' if path[-1][0] == '<' else '<') + path[-1][1:])

with open(forbidden_ends_file) as f:
	for l in f:
		parts = l.strip().split(',')
		for part in parts:
			if part in resolvable_ends: resolvable_ends.remove(part)

sys.stderr.write(str(len(resolvable_ends)) + " resolvable ends\n")
sys.stderr.write(str(resolvable_ends) + "\n")

node_seq = {}

with open(graph_file) as f:
	for l in f:
		parts = l.strip().split('\t')
		if parts[0] == 'S':
			node_seq[parts[1]] = parts[2]
		elif parts[0] == 'L':
			check_from = (">" if parts[2] == "+" else "<") + parts[1]
			check_to = ("<" if parts[4] == "+" else ">") + parts[3]
			if check_from in resolvable_ends or check_to in resolvable_ends:
				continue
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
		if len(path) == 0: continue
		if path[0] not in resolvable_ends or ((">" if path[-1][0] == "<" else "<") + path[-1][1:]) not in resolvable_ends: continue
		sys.stderr.write("insert path " + str(path) + "\n")
		last_node = path[0]
		for i in range(1, len(path)-1):
			if path[i][1:] not in num_insertions: num_insertions[path[i][1:]] = 0
			num_insertions[path[i][1:]] += 1
			this_node = path[i][0] + path[i][1:] + "_" + str(num_insertions[path[i][1:]])
			print("S\t" + this_node[1:] + "\t" + node_seq[path[i][1:]])
			print("L\t" + last_node[1:] + "\t" + ("+" if last_node[0] == ">" else "-") + "\t" + this_node[1:] + "\t" + ("+" if this_node[0] == ">" else "-") + "\t0M")
			last_node = this_node
		print("L\t" + last_node[1:] + "\t" + ("+" if last_node[0] == ">" else "-") + "\t" + path[-1][1:] + "\t" + ("+" if path[-1][0] == ">" else "-") + "\t0M")
