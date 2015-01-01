#!/usr/bin/python

import sys
import os
import Image

HELP = '''Imagegrid - Tool for generating grid image from tiles
Author: niwi.cz, 2013
Usage:
imagegrid.py /dir/with/tiles'''

COLS = 10
ROWS = 8
TILE_WIDTH = 81
TILE_HEIGHT = 81
TILE_MARGIN = 7
OUTPUT_FILE = "grid.jpg"

# check arg
if len(sys.argv) < 2:
  print HELP
  exit(1)
#endif
path = sys.argv[1]
if path[len(path)-1] != '/':
  path += '/'
#endif

# list dir
filenames = []
try:
  filenames = sorted(os.listdir(path))
except:
  print "Wrong directory name!"
  exit(1)
#endtry
tileCount = len(filenames)
print "Tiles found: %s" % tileCount

# create image
img = Image.new("RGB", (COLS*(TILE_WIDTH+2*TILE_MARGIN), ROWS*(TILE_HEIGHT+2*TILE_MARGIN)), "#DDDDDD")
# add tiles
for x in range(COLS):
  for y in range(ROWS):
    if y*ROWS+x >= tileCount:
      break;	# na druhy cyklus kaslem:)
    #endif
    tile = Image.open(path + filenames[y*ROWS+x])
    img.paste(tile, (TILE_MARGIN+x*(TILE_WIDTH+2*TILE_MARGIN), TILE_MARGIN+y*(TILE_HEIGHT+2*TILE_MARGIN)))
#endfor

# save image to the program directory
img.save(OUTPUT_FILE)
print "Saved to the file: %s" % OUTPUT_FILE
