#!/usr/bin/python

import sys

# gaf from stdin
# colors from args pj13=red dj13=lightred etc
# latter has priority

recolor = {}
color_priority = {}

for arg in sys.argv[1:]:
	parts = arg.strip().split('=')
	recolor[parts[0]] = parts[1]
	color_priority[parts[0]] = len(color_priority)

node_colors = {}

for l in sys.stdin:
	parts = l.strip().split('\t')
	pathnodes = parts[5].replace('>', '\t').replace('<', '\t').split('\t')
	name = parts[0].split(' ')[0]
	if name not in recolor: continue
	color = recolor[name]
	priority = color_priority[name]
	for node in pathnodes:
		if node not in node_colors: node_colors[node] = (priority, color, name)
		if priority > node_colors[node][0]: node_colors[node] = (priority, color, name)

print("Node,Alignment,Colour")
for n in node_colors:
	print(n + "," + node_colors[n][2] + "," + node_colors[n][1])
