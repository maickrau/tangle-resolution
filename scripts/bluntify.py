#!/usr/bin/python

import sys
import fileinput

# gfa graph from stdin or filename
# gfa graph to stdout

def revcomp(s):
	comp = { 'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C' }
	return "".join(comp[c] for c in s[::-1])

def canon_tip_direction(n1, n2):
	fw = (n1, n2)
	bw = (n2, n1)
	fwstr = fw[0][0] + fw[0][1] + fw[1][0] + fw[1][1]
	bwstr = bw[0][0] + bw[0][1] + bw[1][0] + bw[1][1]
	if bwstr < fwstr: return bw
	return fw

node_lines = []
edge_lines = []
has_edge = {}
max_overlap = {}
node_seqs = {}
has_path = False
for l in fileinput.input():
	parts = l.strip().split('\t')
	if parts[0] == 'S':
		node_lines.append(l.strip())
		node_seqs[parts[1]] = parts[2]
	elif parts[0] == 'L':
		if len(parts) < 6:
			sys.stderr.write(l.strip() + '\n')
			sys.exit("Edge couldn't be parsed")
		if parts[5] == "*":
			sys.exit("Graphs with * overlaps are not supported")
		if parts[5][-1] != "M":
			sys.stderr.write(l.strip() + '\n')
			sys.exit("Overlap couldn't be parsed: " + parts[5])
		fromtip = (parts[1], parts[2])
		totip = (parts[3], "-" if parts[4] == "+" else "+")
		overlap = int(parts[5][:-1])
		key = (canon_tip_direction(fromtip, totip), overlap)
		if key in has_edge:
			old = has_edge[key]
			oldparts = old.strip().split('\t')
			match = True
			if len(parts) != len(oldparts):
				match = False
			for i in range(6, min(len(parts), len(oldparts))):
				if parts[i] != oldparts[i]:
					match = False
			if not match:
				sys.stderr.write("Warning: duplicate edges with different tags.\n")
				sys.stderr.write("The first edge of the following has been added and the second discarded:\n")
				sys.stderr.write(old + "\n")
				sys.stderr.write(l.strip() + "\n")
			continue
		edge_lines.append(l.strip())
		has_edge[key] = l.strip()
		if fromtip not in max_overlap: max_overlap[fromtip] = overlap
		if totip not in max_overlap: max_overlap[totip] = overlap
		max_overlap[fromtip] = max(max_overlap[fromtip], overlap)
		max_overlap[totip] = max(max_overlap[totip], overlap)
	elif parts[0] == 'H':
		print(l.strip())
	elif parts[0] == 'P':
		has_path = True

if has_path:
	sys.stderr.write("Warning: paths are currently not supported. Paths have been discarded from the output graph\n")

for n in node_lines:
	parts = n.split('\t')
	node_id = parts[1]
	seq = parts[2]
	max_start_overlap = 0
	max_end_overlap = 0
	if (node_id, "-") in max_overlap: max_start_overlap = max_overlap[(node_id, "-")]
	if (node_id, "+") in max_overlap: max_end_overlap = max_overlap[(node_id, "+")]
	start_clip = (max_start_overlap+1) / 2
	end_clip = (max_end_overlap+1) / 2
	if end_clip > 0: 
		seq = seq[start_clip:-end_clip]
	else:
		seq = seq[start_clip:]
	assert len(seq) > 0
	parts[2] = seq
	print("\t".join(parts))

for e in edge_lines:
	parts = e.split('\t')
	overlap = int(parts[5][:-1])
	fromtip = (parts[1], parts[2])
	totip = (parts[3], "-" if parts[4] == "+" else "+")
	assert max_overlap[fromtip] >= overlap
	assert max_overlap[totip] >= overlap
	from_clip = (max_overlap[fromtip]+1) / 2
	to_clip = (max_overlap[totip]+1) / 2
	if from_clip + to_clip == overlap:
		parts[5] = "0M"
		print("\t".join(parts))
		continue
	assert from_clip + to_clip > overlap
	missing_length = from_clip + to_clip - overlap
	assert missing_length > 0
	if from_clip + to_clip < missing_length:
		sys.stderr.write(str(fromtip) + " " + str(totip) + " " +str(from_clip) + " " + str(to_clip) + " " + str(overlap) + " " + str(missing_length) + "\n")
	assert from_clip + to_clip >= missing_length
	missing_seq = node_seqs[fromtip[0]]
	if fromtip[1] == "-": missing_seq = revcomp(missing_seq)
	assert from_clip < len(missing_seq)
	if missing_length <= from_clip:
		missing_seq = missing_seq[-from_clip : -from_clip+missing_length]
	else:
		missing_seq = missing_seq[-from_clip:]
	still_missing_length = missing_length - len(missing_seq)
	if still_missing_length > 0:
		extra_missing_seq = node_seqs[totip[0]]
		if totip[1] == "+": extra_missing_seq = revcomp(extra_missing_seq)
		assert to_clip < len(extra_missing_seq)
		extra_missing_seq = extra_missing_seq[to_clip-still_missing_length : to_clip]
		missing_seq += extra_missing_seq
	assert len(missing_seq) > 0
	assert len(missing_seq) == missing_length
	fromnode = fromtip
	tonode = (totip[0], "+" if totip[1] == "-" else "-")
	new_node_name = "edgeseq_" + fromnode[0] + "_" + ("fw" if fromnode[1] == "+" else "bw") + "_" + tonode[0] + "_" + ("fw" if tonode[1] == "+" else "bw")
	print("S\t" + new_node_name + "\t" + missing_seq)
	print("L\t" + fromnode[0] + "\t" + fromnode[1] + "\t" + new_node_name + "\t+\t0M")
	print("L\t" + new_node_name + "\t+\t" + tonode[0] + "\t" + tonode[1] + "\t0M")

