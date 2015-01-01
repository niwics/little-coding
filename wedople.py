#!/usr/bin/python

# Script for generating HTML list items with guests for our wedding
# author: niwi.cz, August 2014

from random import shuffle

filename = "svatebni-hoste-vizitky.txt"

with open(filename) as f:
    content = f.readlines()

new_person = True
sex = None
items = []
for line in content:
    line = line.strip()
    if line == "###":
        break
    if line == "??":
        continue
    if line in ("M", "F", "??"):
	sex = line
        continue
    if not line:
        new_person = True
        continue
    if new_person:
        # ignore the name
        new_person = False
	continue
    items.append((line, sex))

shuffle(items)

for text, sex in items:
    print "<li class=\"%s\">%s</li>" % (sex, text)
