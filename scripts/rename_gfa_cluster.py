#!/usr/bin/python

import sys

# clusters in argv
# graph in stdin

belongs_to_cluster = {}

for i in range(1, len(sys.argv)):
    with open(sys.argv[i]) as f:
        for l in f:
            belongs_to_cluster[l.strip()] = i

for l in sys.stdin:
    parts = l.strip().split('\t')
    if l[0] == 'S':
        if parts[1] in belongs_to_cluster:
            parts[1] = "clust" + str(belongs_to_cluster[parts[1]]) + "_" + parts[1]
    if l[0] == 'L':
        if parts[1] in belongs_to_cluster:
            parts[1] = "clust" + str(belongs_to_cluster[parts[1]]) + "_" + parts[1]
        if parts[3] in belongs_to_cluster:
            parts[3] = "clust" + str(belongs_to_cluster[parts[3]]) + "_" + parts[3]
    print("\t".join(parts))

