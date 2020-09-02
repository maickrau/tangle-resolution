#!/usr/bin/python

import sys
import re

round_number = sys.argv[1]
readlens_file = sys.argv[2]

def print_matches(readname, matches, files):
	cluster_contiguous = {}
	for cluster in matches:
		matches[cluster].sort(key=lambda x: x[1])
		contiguous_start = matches[cluster][0][0]
		contiguous_end = matches[cluster][0][1]
		for match in matches[cluster]:
			if match[0] > contiguous_end:
				if cluster not in cluster_contiguous: cluster_contiguous[cluster] = []
				cluster_contiguous[cluster].append((contiguous_start, contiguous_end))
				contiguous_start = match[0]
				contiguous_end = match[1]
			else:
				contiguous_end = match[1]
		if cluster not in cluster_contiguous: cluster_contiguous[cluster] = []
		cluster_contiguous[cluster].append((contiguous_start, contiguous_end))
	has_cluster_noncontained = set()
	for cluster in cluster_contiguous:
		for contiguous in cluster_contiguous[cluster]:
			contained = False
			for cluster2 in cluster_contiguous:
				if cluster2 == cluster: continue
				for contiguous2 in cluster_contiguous[cluster2]:
					if contiguous2[0] <= contiguous[0] and contiguous2[1] >= contiguous[1]:
						contained = True
						break
				if contained: break
			if not contained:
				has_cluster_noncontained.add(cluster)
				continue
	if len(has_cluster_noncontained) != 1: return
	for cluster in has_cluster_noncontained:
		files[cluster].write(readname + "\n")

readlens = {}

with open(readlens_file) as f:
	for l in f:
		parts = l.strip().split('\t')
		readlens[parts[0].split(' ')[0]] = int(parts[1])

readname = ""
matches = {}
fw = True


with open("readnames_cluster0_round" + round_number + ".txt", "w") as f0:
	with open("readnames_cluster1_round" + round_number + ".txt", "w") as f1:
		with open("readnames_cluster2_round" + round_number + ".txt", "w") as f2:
			with open("readnames_cluster3_round" + round_number + ".txt", "w") as f3:
				with open("readnames_cluster4_round" + round_number + ".txt", "w") as f4:
					files = [f0, f1, f2, f3, f4]
					for l in sys.stdin:
						if l[0] == '>':
							new_readname = l[2:].strip()
							fw = True
							if len(new_readname) > len(" Reverse") and new_readname[-len(" Reverse"):] == " Reverse":
								new_readname = new_readname[:-len(" Reverse")]
								fw = False
							if new_readname != readname:
								print_matches(readname, matches, files)
								matches = {}
								readname = new_readname
						else:
							parts = re.sub(" +", " ", l.strip()).split(' ')
							contig = parts[0]
							assert len(contig) > len("cluster0_")
							assert contig[0:len("cluster")] == "cluster"
							assert contig[8] == "_"
							cluster = int(contig[7])
							if fw:
								match_start = int(parts[2])
								match_end = int(parts[2]) + int(parts[3])
							else:
								match_start = readlens[readname] - int(parts[2]) - int(parts[3]) + 2
								match_end = match_start + int(parts[3])
							if cluster not in matches: matches[cluster] = []
							matches[cluster].append((match_start, match_end))
					print_matches(readname, matches, files)
