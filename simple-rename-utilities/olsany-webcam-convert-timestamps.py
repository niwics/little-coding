#!/usr/bin/python

# Script for renaming images (timestamps) loaded from Olsany webcam: http://www.drvrkam.vys.cz/kamera.php?id=8
# author: niwi.cz, 2015-01-01

from sys import argv
import os, os.path
import re
from datetime import datetime
from shutil import copy2

WEBCAM_IMG_PATTERN = r"\d+@(\d+).jpg"

if len(argv) != 2:
    print "Usage: %s /path/to/source_images_folder" % argv[0]
    exit(1)

dir = argv[1]

for root, dirs, files in os.walk(dir):
    for f in files:
        m = re.match(WEBCAM_IMG_PATTERN, f)
        if not m:
            print "ERROR: File %s does not match the webcam file pattern %s." % (f, WEBCAM_IMG_PATTERN)
        timestamp = m.group(1)
        iso_date = datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        print "Converting %s to %s..." % (timestamp, iso_date)
        copy2(dir+"/"+f, dir+"/olsany-webcam-%s.jpg" % iso_date)

