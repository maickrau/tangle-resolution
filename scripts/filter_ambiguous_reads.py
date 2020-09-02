#!/usr/bin/python

import sys

ambiguous_file = sys.argv[1]
#gaf from stdin

ambiguous = set()
with open(ambiguous_file) as f:
    for l in f:
        ambiguous.add(l.strip())

for l in sys.stdin:
    parts = l.strip().split('\t')
    name = parts[0].split(' ')[0]
    if name in ambiguous: continue
    print(l.strip())

