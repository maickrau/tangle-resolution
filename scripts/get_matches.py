#!/usr/bin/python

import sys
import re

min_match = int(sys.argv[1])


def get_overlap(matches):
    matches.sort(key=lambda x: x[0])
    last_match_end = 0
    overlap = 0
    for match in matches:
        match_end = match[0] + match[1]
        overlap += min(match[1], match_end - last_match_end)
        last_match_end = match_end
    return overlap

last_read = ""
matches = []
for l in sys.stdin:
    if l[0] == '>':
        read_name = l[1:].strip().split(' ')[0]
        if read_name != last_read:
            overlap = get_overlap(matches)
            if overlap >= min_match:
                print(last_read + "\t" + str(overlap))
            matches = []
        last_read = read_name
        continue
    parts = re.sub(" +", " ", l.strip()).split(' ')
    pos = parts[2]
    matchlen = parts[3]
    matches.append((int(pos), int(matchlen)))
overlap = get_overlap(matches)
if overlap >= min_match: print(last_read + "\t" + str(overlap))
