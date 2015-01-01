#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Find all bands from my library related to Glasgow.
# Performs simple fulltext search on Wikipedia.

# author niwi.cz, March 2013

import sys
import os
import time
import httplib
import urllib2

DEBUG = True
SEARCH_FOR = 'Glasgow'
AUDIO_FOLDER = '/media/terka2/Audio/alba'
WIKI_LINK = 'http://en.wikipedia.org/wiki/'


def err(message):
    print >> sys.stderr, message
#enddef

# fake user-agent for urllib (without this setting Wikipedia returns 403)
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/10.0')]

# scan directory folders
founded = []
for root, dirs, files in os.walk(AUDIO_FOLDER):
    for dirname in dirs:
        link = (WIKI_LINK + dirname).replace(' ', '_')
        if DEBUG:
            sys.stdout.write('\nSearching in ' + link + '...')
        #€ndif
        try:
            res = opener.open(link)
        except urllib2.HTTPError, e:
            if e.code != 404:
                err('HTTPError = ' + str(e.code))
            #endif
            continue
        except urllib2.URLError, e:
            err('URLError = ' + str(e.reason))
            continue
        except httplib.HTTPException, e:
            err('HTTPException')
            continue
        #endtry
        page = res.read();
        index = page.find(SEARCH_FOR)
        if index != -1:
            founded.append(dirname)
            fromIndex = max(index-25, 0)
            sys.stdout.write(' FOUNDED: "' + page[fromIndex : fromIndex+60] +  '"')
        #endif
        time.sleep(1)
    #endfor
    del dirs[:]  # do not recurse
#endfor

# Finaly print out all founded artists
print "\n\nRESULT\n------\n" + "\n".join(founded)

