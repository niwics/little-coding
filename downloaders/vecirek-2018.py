#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author: niwi.cz, December 2018

import sys
import os
import re
import time
import requests

INFILE = 'vecirek.html'
OUT_DIR = 'vecirek'


def err(message):
    print >> sys.stderr, message


def main():

    # parse the image addresses
    f = open(INFILE)
    source_string = f.read()

    # found images
    matches = re.findall(" href=\"(https://foto.seznamakce.cz/wp-content/uploads/2018/12/SOFTV\d-20181206(\d\d)(\d\d)([0-9\-]+)\.jpg)", source_string)
    print "Downloading %s files..." % len(matches)

    file_num = 0
    # download these images
    for match in matches:
        file_num += 1
        print "Downloading %s..." % match[0]
        r = requests.get(match[0])
        of = open("%s/%s-%s-%s.jpg" % (OUT_DIR, match[1], match[2], match[3]), 'w')
        of.write(r.content)
        time.sleep(0.1)

    print "%s files were downloaded to %s." % (file_num, OUT_DIR)


if __name__ == '__main__':
    main()
