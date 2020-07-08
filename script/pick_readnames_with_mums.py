#!/usr/bin/python

import fileinput

lastread = ""
lastprunt = ""

for l in fileinput.input():
    if l[0] == '>':
        lastread = l[1:].strip()
        if len(lastread) > 8 and lastread[-8:] == " Reverse":
            lastread = lastread[:-8]
    else:
        if lastread != lastprunt:
            print(lastread)
            lastprunt = lastread

