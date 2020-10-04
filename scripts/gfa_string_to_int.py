#!/usr/bin/python

import sys

output_mapping_file = sys.argv[1]
# input graph from stdin
# output graph to stdout

nodenumbers = {}
nextnumber = 1

for line in sys.stdin:
	l = line.strip()
	if len(l) == 0: print(l)
	if l[0] == 'S':
		parts = l.split('\t')
		if parts[1] not in nodenumbers:
			nodenumbers[parts[1]] = nextnumber
			nextnumber += 1
		parts[1] = str(nodenumbers[parts[1]])
		print('\t'.join(parts))
	if l[0] == 'L':
		parts = l.split('\t')
		if parts[1] not in nodenumbers:
			nodenumbers[parts[1]] = nextnumber
			nextnumber += 1
		if parts[3] not in nodenumbers:
			nodenumbers[parts[3]] = nextnumber
			nextnumber += 1
		parts[1] = str(nodenumbers[parts[1]])
		parts[3] = str(nodenumbers[parts[3]])
		print('\t'.join(parts))

outputmapping = [(node_id, nodenumbers[node_id]) for node_id in nodenumbers]
outputmapping.sort(key= lambda x: x[1])
with open(output_mapping_file, 'w') as f:
	for mapping in outputmapping:
		f.write(mapping[0] + '\n')
