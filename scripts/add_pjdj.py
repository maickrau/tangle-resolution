#!/usr/bin/python

import sys

graphfile = sys.argv[1]
gaffile = sys.argv[2]
seqfile = sys.argv[3]
# graph to stdout

def revcomp(s):
    comp = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    return "".join(comp[c] for c in s[::-1])

seq = {}
current_seq = ""
current_name = ""
with open(seqfile) as f:
    for l in f:
        if l[0] == '>':
            if current_name != "":
                seq[current_name] = current_seq
            current_name = l[1:].strip().split(' ')[0]
            current_seq = ""
        else:
            current_seq += l.strip()
seq[current_name] = current_seq

nodelens = {}
with open(graphfile) as f:
    for l in f:
        if l[0] == 'S':
            parts = l.strip().split('\t')
            nodelens[parts[1]] = len(parts[2])

additions = []
broken = set()

with open(gaffile) as f:
    for l in f:
        parts = l.strip().split('\t')
        path = []
        pathstr = parts[5] + '>'
        last_break = 0
        name = parts[0].split(' ')[0]
        for i in range(1, len(pathstr)):
            if pathstr[i] == '<' or pathstr[i] == '>':
                path.append(pathstr[last_break:i])
                last_break = i
        if parts[2] != "0":
            offset = int(parts[7])
            direction = path[0][0] == '>'
            additions.append((seq[name][0:int(parts[2])], path[0][1:], direction, offset, True, name))
            broken.add(path[0][1:])
        if parts[3] != parts[1]:
            right_clip = int(parts[6]) - int(parts[8])
            offset = nodelens[path[-1][1:]] - right_clip
            direction = path[-1][0] == '>'
            additions.append((revcomp(seq[name][int(parts[3]):]), path[-1][1:], not direction, nodelens[path[-1][1:]] - offset - 1, True, name))
            broken.add(path[-1][1:])

fw_in = {}
bw_in = {}

with open(graphfile) as f:
    for l in f:
        parts = l.strip().split('\t')
        if parts[0] == 'S':
            if parts[1] not in broken:
                print("\t".join(parts))
                continue
            fw_breakpoints = []
            for addition in additions:
                if addition[1] != parts[1]: continue
                if addition[2]:
                    fw_breakpoints.append(addition[3])
                else:
                    fw_breakpoints.append(nodelens[parts[1]] - addition[3])
            fw_breakpoints.sort()
            assert len(fw_breakpoints) >= 1
            if fw_breakpoints[-1] == nodelens[parts[1]]:
                fw_breakpoints = fw_breakpoints[:-1]
                bw_in[(parts[1], 0)] = parts[1] + "_end"
            if len(fw_breakpoints) > 0 and fw_breakpoints[0] == 0:
                fw_breakpoints = fw_breakpoints[1:]
            if len(fw_breakpoints) == 0:
                fw_breakpoints.append(1) # fake!
                assert nodelens[parts[1]] >= 2
                fw_in[(parts[1], 0)] = parts[1] + "_0"
            assert len(fw_breakpoints) >= 1
            last_break = 0
            for i in fw_breakpoints:
                print("S\t" + parts[1] + "_" + str(last_break) + "\t" + parts[2][last_break:i])
                fw_in[(parts[1], i)] = parts[1] + "_" + str(i)
                bw_in[(parts[1], nodelens[parts[1]] - i)] = parts[1] + "_" + str(last_break)
                last_break = i
            fw_in[(parts[1], last_break)] = parts[1] + "_end"
            print("S\t" + parts[1] + "_end\t" + parts[2][last_break:])
            last_break = 0
            for i in fw_breakpoints[:-1]:
                print("L\t" + parts[1] + "_" + str(last_break) + "\t+\t" + parts[1] + "_" + str(i) + "\t+\t0M")
                last_break = i
            print("L\t" + parts[1] + "_" + str(last_break) + "\t+\t" + parts[1] + "_end\t+\t0M")
        if parts[0] == 'L':
            if parts[1] in broken:
                if parts[2] == "+":
                    parts[1] = parts[1] + "_end"
                else:
                    parts[1] = parts[1] + "_0"
            if parts[3] in broken:
                if parts[4] == "+":
                    parts[3] = parts[3] + "_0"
                else:
                    parts[3] = parts[3] + "_end"
            print("\t".join(parts))

next_id = 1
for addition in additions:
    print("S\ttip_" + str(next_id) + "\t" + addition[0])
    tip_dir = "+" if addition[4] else "-"
    trunk_dir = bool(addition[2]) == bool(addition[4]) 
    if trunk_dir:
        print("L\ttip_" + str(next_id) + "\t" + tip_dir + "\t" + fw_in[(addition[1], addition[3])] + "\t+\t0M")
    else:
        print("L\ttip_" + str(next_id) + "\t" + tip_dir + "\t" + bw_in[(addition[1], addition[3])] + "\t-\t0M")
    next_id += 1


