#!/usr/bin/python

import sys

graphfile = sys.argv[1]
min_coverage = int(sys.argv[2])
# tips from stdin

def reverse(n):
	return ("<" if n[0] == ">" else ">") + n[1:]

node_seqs = {}
new_edges = []
node_fw_breakpoints = {}
unique_edge = {}

with open(graphfile) as f:
	for l in f:
		parts = l.strip().split('\t')
		if l[0] == 'S':
			node_seqs[parts[1]] = parts[2].strip()
			node_fw_breakpoints[parts[1]] = set()
			node_fw_breakpoints[parts[1]].add(0)
			node_fw_breakpoints[parts[1]].add(len(node_seqs[parts[1]]))
		if l[0] == 'L':
			assert parts[1] in node_seqs
			assert parts[3] in node_seqs
			fromnode = ""
			if parts[2] == "+":
				fromnode = ">" + parts[1]
			else:
				fromnode = "<" + parts[1]
			tonode = ""
			if parts[4] == "+":
				tonode = ">" + parts[3]
			else:
				tonode = "<" + parts[3]
			new_edges.append((fromnode, len(node_seqs[parts[1]]), tonode, 0, ""))
			if fromnode not in unique_edge:
				unique_edge[fromnode] = tonode
			else:
				if unique_edge[fromnode] != tonode: unique_edge[fromnode] = None
			if reverse(tonode) not in unique_edge:
				unique_edge[reverse(tonode)] = reverse(fromnode)
			else:
				if unique_edge[reverse(tonode)] != reverse(fromnode): unique_edge[reverse(tonode)] = None

for l in sys.stdin:
	parts = l.strip().split('\t')
	assert len(parts) == 6
	seqs = {}
	for s in parts[5].split(','):
		if s not in seqs: seqs[s] = 0
		seqs[s] += 1
	maximum = 0
	for s in seqs:
		maximum = max(maximum, seqs[s])
	if maximum < min_coverage: continue
	limit = maximum / 2
	if limit < min_coverage: limit = min_coverage
	for seq in seqs:
		if seqs[seq] < limit: continue
		fromnode = parts[0]
		frompos = int(parts[1])
		tonode = parts[2]
		topos = int(parts[3])
		if seq == "0":
			new_edges.append((fromnode, frompos + 1, tonode, topos, ""))
		elif seq[0] == '-':
			overlap = -int(seq)
			from_min = frompos
			if frompos >= overlap:
				from_min = overlap
			overlap -= from_min
			frompos = frompos - from_min
			if overlap > 0 and len(node_seqs[tonode[1:]]) < topos + overlap:
				while True:
					if overlap == 0: break
					if reverse(fromnode) in unique_edge and unique_edge[reverse(fromnode)] is not None:
						assert frompos == 0
						fromnode = reverse(unique_edge[reverse(fromnode)])
						frompos = len(node_seqs[fromnode[1:]])
						from_min = frompos
						if frompos >= overlap:
							from_min = overlap
						overlap -= from_min
						frompos = frompos - from_min
						continue
					else:
						break
			to_plus = len(node_seqs[tonode[1:]]) - topos
			if to_plus >= overlap:
				to_plus = overlap
			overlap -= to_plus
			topos = topos + to_plus
			if overlap > 0 and len(node_seqs[tonode[1:]]) < topos + overlap:
				while True:
					if overlap == 0: break
					if tonode in unique_edge and unique_edge[tonode] is not None:
						assert topos == len(node_seqs[tonode[1:]])
						tonode = unique_edge[tonode]
						topos = 0
						to_plus = len(node_seqs[tonode[1:]])
						if to_plus >= overlap:
							to_plus = overlap
						overlap -= to_plus
						topos = topos + to_plus
						continue
					else:
						break
			if overlap > 0:
				sys.stderr.write("Couldn't connect edge: " + l.strip() + "\n")
				continue
			assert len(node_seqs[tonode[1:]]) >= topos + overlap
			new_edges.append((fromnode, frompos + 1, tonode, topos, ""))
		else:
			new_edges.append((fromnode, frompos + 1, tonode, topos, seq))


for e in new_edges:
	if e[0][0] == '>':
		node_fw_breakpoints[e[0][1:]].add(e[1])
	else:
		assert len(node_seqs[e[0][1:]]) >= e[1]
		node_fw_breakpoints[e[0][1:]].add(len(node_seqs[e[0][1:]]) - e[1])
	if e[2][0] == '>':
		node_fw_breakpoints[e[2][1:]].add(e[3])
	else:
		assert len(node_seqs[e[2][1:]]) > e[3]
		node_fw_breakpoints[e[2][1:]].add(len(node_seqs[e[2][1:]]) - e[3])

outgoing_node_mapping = {}
incoming_node_mapping = {}
new_nodes = {}
new_node_poses = {}
next_id = 1
for n in node_fw_breakpoints:
	fw_breakpoints = list(node_fw_breakpoints[n])
	fw_breakpoints.sort()
	for i in range(1, len(fw_breakpoints)):
		new_nodes[str(next_id)] = node_seqs[n][fw_breakpoints[i-1]:fw_breakpoints[i]]
		new_node_poses[str(next_id)] = n + "_" + str(fw_breakpoints[i-1]) + "_" + str(fw_breakpoints[i])
		incoming_node_mapping[(">" + n, fw_breakpoints[i-1])] = (str(next_id), True)
		outgoing_node_mapping[(">" + n, fw_breakpoints[i])] = (str(next_id), True)
		incoming_node_mapping[("<" + n, len(node_seqs[n]) - fw_breakpoints[i])] = (str(next_id), False)
		outgoing_node_mapping[("<" + n, len(node_seqs[n]) - fw_breakpoints[i-1])] = (str(next_id), False)
		if fw_breakpoints[i] != len(node_seqs[n]):
			new_edges.append((">" + n, fw_breakpoints[i], ">" + n, fw_breakpoints[i], ""))
		next_id += 1


for node in new_nodes:
	print("S\t" + str(node) + "\t" + new_nodes[node] + "\tor:Z:" + str(new_node_poses[node]))

for e in new_edges:
	fromnode = outgoing_node_mapping[(e[0], e[1])]
	tonode = incoming_node_mapping[(e[2], e[3])]
	if e[4] == "":
		print("L\t" + str(fromnode[0]) + "\t" + ("+" if fromnode[1] else "-") + "\t" + str(tonode[0]) + "\t" + ("+" if tonode[1] else "-") + "\t0M")
	else:
		print("S\t" + str(next_id) + "\t" + e[4])
		print("L\t" + str(fromnode[0]) + "\t" + ("+" if fromnode[1] else "-") + "\t" + str(next_id) + "\t+\t0M")
		print("L\t" + str(next_id) + "\t+\t" + str(tonode[0]) + "\t" + ("+" if tonode[1] else "-") + "\t0M")
		next_id += 1

