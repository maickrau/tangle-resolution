#!/usr/bin/python

import sys

graphfile = sys.argv[1]
readsfile = sys.argv[2]
gaffile = sys.argv[3]

def parse_path(s):
	l = s.strip()+'>'
	last_break = 0
	path = []
	for i in range(1, len(l)):
		if l[i] == '<' or l[i] == '>':
			path.append((l[last_break+1:i], l[last_break] == '>'))
			last_break = i
	return path

def revcomp(s):
	comp = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
	return "".join(comp[c] for c in s[::-1])

nodeseqs = {}

with open(graphfile) as f:
	for l in f:
		if l[0] == 'S':
			parts = l.strip().split('\t')
			nodeseqs[parts[1]] = parts[2]

corrections = {}

with open(gaffile) as f:
	for l in f:
		parts = l.strip().split('\t')
		readname = parts[0].split(' ')[0]
		start = int(parts[2])
		end = int(parts[3])
		path = parse_path(parts[5])
		corrected_seq = ""
		for n in path:
			add = nodeseqs[n[0]]
			if not n[1]: add = revcomp(add)
			corrected_seq += add
		assert len(corrected_seq) == int(parts[6])
		corrected_seq = corrected_seq[int(parts[7]):int(parts[8])]
		if readname not in corrections: corrections[readname] = []
		corrections[readname].append((start, end, corrected_seq))

with open(readsfile) as f:
	while True:
		nameline = f.readline().strip()
		seq = f.readline().strip()
		if not nameline or not seq: break
		name = nameline[1:].split(' ')[0]
		if name not in corrections: continue
		corrs = corrections[name]
		corrs.sort(key=lambda x: x[0])
		last_corrected = 0
		corrected_seq = ""
		for c in corrs:
			if c[0] > last_corrected and last_corrected != 0:
				corrected_seq += seq[last_corrected:c[0]-1]
			if c[0] < last_corrected:
				if c[1] < last_corrected: continue
				correction_start = int(float(last_corrected - c[0]) / float(c[1] - c[0]) * len(c[2]))
				corrected_seq += c[2][correction_start:]
				last_corrected = c[1]
				continue
			corrected_seq += c[2]
			last_corrected = c[1]
		print(">" + name)
		print(corrected_seq)
