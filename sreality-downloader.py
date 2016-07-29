#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Download images for sreality.cz.
# URL could not be used, because source pages are dynamic (using Angular),
# so it is necessary to paste the gallery HTML fragment into the temporal file and parse data from it.
#
# author: niwi.cz, January 2016

import sys
import os
import re
import time
import requests

DEBUG = True
DEFAULT_OUT_DIR = '/tmp'
HELP = ("Sreality images downloader - \n\
Author: niwi.cz, 2016\n\
Usage:\n\
%s /file/with/html [outdir]" % sys.argv[0])


def err(message):
    print >> sys.stderr, message


def download(infile, outdir, debug):
    if DEBUG:
        print "Downloading images to the directory: %s" % outdir

    # create the output directory if necessary
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    # parse the image addresses
    f = open(infile)
    source_string = f.read()

    # found images
    matches = re.findall(" src=\"http://img\.sreality\.cz/dyn/dyn/w\d+h\d+/([a-z0-9]+/[a-z0-9]+/[a-z0-9]+/[a-z0-9]+)", source_string)
    if DEBUG:
        print "Downloading %s files..." % len(matches)

    file_num = 0
    # download these images
    for img_name in matches:
        file_num += 1
        img_url = "http://img.sreality.cz/big/dyn/%s" % img_name
        r = requests.get(img_url)
        of = open("%s/%02d.jpg" % (outdir, file_num), 'w')
        of.write(r.content)
        time.sleep(0.2)

    print "%s files were downloaded to %s." % (file_num, outdir)


def main():
    # check args
    if len(sys.argv) < 2:
        print HELP
        exit(1)
    infile = sys.argv[1]

    outdir = DEFAULT_OUT_DIR
    if len(sys.argv) > 2:
        outdir = sys.argv[2]

    download(infile, outdir, DEBUG)

if __name__ == '__main__':
    main()
