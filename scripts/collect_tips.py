#!/usr/bin/python

import sys

readfile = sys.argv[1]
graphfile = sys.argv[2]
# alignments from stdin

def parse_path(s):
	l = s.strip()+'>'
	last_break = 0
	path = []
	for i in range(1, len(l)):
		if l[i] == '<' or l[i] == '>':
			path.append((l[last_break+1:i], l[last_break] == '>'))
			last_break = i
	return path

def canon(n1, n2):
	fw = (n1, n2)
	bw = ((n2[0], not n2[1]), (n1[0], not n1[1]))
	if fw < bw: return fw
	return bw

def format(n):
	return (">" if n[1] else "<") + n[0]

node_lens = {}
with open(graphfile) as f:
	for l in f:
		if l[0] == 'S':
			parts = l.strip().split('\t')
			node_lens[parts[1]] = len(parts[2])

read_seqs = {}
with open(readfile) as f:
	while True:
		nameline = f.readline()
		seqline = f.readline()
		if not nameline or not seqline: break
		read_seqs[nameline[1:].split(' ')[0].strip()] = seqline.strip()

last_parts = []
for l in sys.stdin:
	parts = l.strip().split('\t')
	if len(last_parts) == 0:
		last_parts = parts
		continue
	if parts[0] != last_parts[0]:
		last_parts = parts
		continue
	name = parts[0].split(' ')[0].strip()
	last_end = parse_path(last_parts[5])[-1]
	last_seq_end = int(last_parts[3])
	last_node_end = node_lens[last_end[0]] - (int(last_parts[6]) - int(last_parts[8])) - 1
	new_start = parse_path(parts[5])[0]
	new_seq_start = int(parts[2])
	new_node_start = int(parts[7])
	print(format(last_end) + "\t" + str(last_node_end) + "\t" + format(new_start) + "\t" + str(new_node_start) + "\t" + name + "\t" + str(last_seq_end) + "\t" + str(new_seq_start) + "\t" + read_seqs[name][last_seq_end:new_seq_start])
