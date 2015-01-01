#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Miroslav Kvasnica, niwi.cz
# May 2013
#
#
# Output structure:
# FIT - resources - style.css, logo.gif...
#     - study - study.html
#             - COURSE-XXXXXX (ex. TIN-123456) - course.html
#                                              - annotations.html
#                                              - wiki.html
#                                              - event-XXXXXX.html (ex. event-123456.html)
#                                              - graph-XXXXXX.png (ex. graph-123456.png)
import sys
import os
import re
import httplib
import urllib2

DEBUG = True

# login data
WIS_USERNAME = 'xusern00'
WIS_PASSWORD = 'password'

ROOT_DIR_NAME = 'FIT'
RESOURCES_DIR_NAME = 'resources'
# URLs
ROOT_URL = 'https://wis.fit.vutbr.cz'
ROOT_PAGES_URL = 'https://wis.fit.vutbr.cz/FIT/st'
ROOT_WEB_URL = 'https://www.fit.vutbr.cz'
STUDY_SWITCHER_URL = 'https://wis.fit.vutbr.cz/FIT/st/index.php?cist='
COURSE_LIST_URL = 'https://wis.fit.vutbr.cz/FIT/st/study-a.php'
# regexps
COURSE_ROW_RE = re.compile('<tr align=center valign=top bgcolor=[^>]+>(.*)</tr>')
COURSE_CODE_RE = re.compile('<th align=left>(....?)</th>')
COURSE_LINK_RE = re.compile('<a class=bar href="(course-sl.php\?id=(\d+)(&amp;back=a)?)')
COURSE_ANNOTATIONS_RE = re.compile('<a href="(https://www.fit.vutbr.cz/study/courses/index.php\?id=\d+)">Web')
COURSE_WIKI_RE = re.compile('<a href="(cwk.php\?id=\d+)">Wiki')
EVENT_ROW_RE = re.compile('<tr bgcolor=[^>]+>(.*)</tr>')
EVENT_LINK_RE = re.compile('<a href="(/FIT/st/(course-sl.php\?id=\d+&amp;item=(\d+)([^"]+)?))">')
GRAPH_IMAGE_RE = re.compile('<img src="(course-s?g.php\?id=(\d+)([^"]+)?)"')

class CrawlerException(Exception):
    pass
#endclass

class FITCrawler:
    
    def __init__(self):
        """Documentation"""
        
        self.RESOURCES_WIS = {
            # CSS
            'common/style.css': 'style.css',
            # images
            'images/favicon.ico': 'favicon.ico',
            'images/checkbox.gif': 'checkbox.gif',
            'images/checkboxs.gif': 'checkboxs.gif',
            'common/img/fit_cz.gif': 'fit_cz.gif',
            'common/img/globus.gif': 'globus.gif',
            'common/img/flag2_gb.gif': 'flag2_gb.gif'
        }        
        self.RESOURCES_WEB = {
            # CSS
            'common/style/style.css': 'style-web.css',
            # images
            'common/style/images/logo_fit_small.png': 'logo_fit_small.png',
            'common/style/images/search.png': 'search.png',
            # images from CSS file - for download to resources only
            'common/style/images/left_strip.png': 'left_strip.png',
            'common/style/images/right_strip.png': 'right_strip.png',
            'common/style/images/ninsignie_cs.jpg': 'ninsignie_cs.jpg'
        }
        self.RESOURCES = dict(self.RESOURCES_WIS.items() + self.RESOURCES_WEB.items())
    #enddef
        

    def parseAndSave(self):
        
        # create root directory
        try:
            os.mkdir(ROOT_DIR_NAME)
        except OSError, e:
            pass # exists yet => OK
        #endtry
        self.saveResources()
        
        # create a password manager
        passwordMgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passwordMgr.add_password(realm='FIT student',
                                  uri=ROOT_URL,
                                  user=WIS_USERNAME,
                                  passwd=WIS_PASSWORD)
        handler = urllib2.HTTPBasicAuthHandler(passwordMgr)
        opener = urllib2.build_opener(handler)
        # fake user-agent for urllib (without this setting Wikipedia returns 403)
        opener.addheaders = [('User-agent', 'Mozilla/10.0')]
        # ...and install it globally so it can be used with urlopen.
        urllib2.install_opener(opener)

        # iterate over all studies
        for studyNumber in [1, 2, 3]:
            try:
                urllib2.urlopen(STUDY_SWITCHER_URL+str(studyNumber))
            except urllib2.HTTPError, e:
                if e.code != 401:
                    raise CrawlerException('Root page HTTPError = ' + str(e.code))
                else:
                    raise CrawlerException('Authentification required (401): ' + e.hdrs['WWW-Authenticate'])
                #endif
                return False
            except urllib2.URLError, e:
                raise CrawlerException('URLError = ' + str(e.reason))
            except httplib.HTTPException, e:
                raise CrawlerException('HTTPException')
            #endtry

            self.processStudy(studyNumber)
        #endfor
        return True
    #enddef
    

    def processStudy(self, studyNumber):
        
        FITCrawler.dbg('\nProcessing study #%s\n-------------------' % studyNumber)
        
        # create directory for this study
        studyDirname = 'study-' + str(studyNumber)
        try:
            os.mkdir(os.path.join(ROOT_DIR_NAME, studyDirname))
        except OSError, e:
            pass # exists yet => OK
        #endtry
        
        page = FITCrawler.retrieveUrl(COURSE_LIST_URL, 'Study page ')
        replacementsDict = {}
        
        # find all courses table rows
        iterator = COURSE_ROW_RE.finditer(page)
        for rowMatch in iterator:
            row = rowMatch.group(1)
            # get course code
            courseCodeMatch = COURSE_CODE_RE.search(row)
            # get course link
            courseLinkMatch = COURSE_LINK_RE.search(row)
            if not courseLinkMatch:
                continue
            #endif
            courseCode = courseCodeMatch.group(1)
            try:
                courseLink = courseLinkMatch.group(1)
                courseId = courseLinkMatch.group(2)
            except AttributeError:
                print row
                raise CrawlerException('Could not find the course link (course: %s, study no. %s)' % (courseCode, studyNumber))
            #endtry
            replacementsDict[courseLink] = os.path.join(courseCode+'-'+courseId, 'course.html')
            FITCrawler.dbg('Parsing course ' + courseCode + ' (ID: ' + courseId + ')')
            courseDirname = os.path.join('study-' + str(studyNumber), courseCode+'-'+courseId)
            self.processCourse(courseDirname, courseLink)
        #endfor
        
        # replace links in this page
        page = self.replaceLinks(page, replacementsDict, 1)
        # save this page        
        FITCrawler.saveFile(os.path.join(studyDirname, 'study.html'), page)
    #enddef
    

    def processCourse(self, courseDirname, courseLink):
        
        # create sub-directory for this course
        try:
            os.mkdir(os.path.join(ROOT_DIR_NAME, courseDirname))
        except OSError, e:
            pass # exists yet => OK
        #endtry
        
        page = FITCrawler.retrieveUrl(os.path.join(ROOT_PAGES_URL, courseLink), 'Course page ')
        replacementsDict = {}
        
        # find all events table rows
        iterator = EVENT_ROW_RE.finditer(page)
        for rowMatch in iterator:
            row = rowMatch.group(1)
            # get course link
            eventLinkMatch = EVENT_LINK_RE.search(row)
            if not eventLinkMatch:
                continue
            #endif
            eventLinkFull = eventLinkMatch.group(1)
            eventLinkShort = eventLinkMatch.group(2)
            eventId = eventLinkMatch.group(3)
            replacementsDict[eventLinkFull] = 'event-%s.html'%eventId
            FITCrawler.dbg('  Parsing event ' + eventId + ' (courseDirname: ' + courseDirname + ')')
            self.processEvent(courseDirname, eventId, eventLinkShort)
        #endfor 
        
        # replace links in this page
        page = self.replaceLinks(page, replacementsDict, 2)
        # save graph + subpages and replace its links
        page = self.handleGraphAndSubpages(page, courseDirname, True)
        # save this page
        FITCrawler.saveFile(os.path.join(courseDirname, 'course.html'), page)
    #enddef
    

    def processEvent(self, courseDirname, eventId, eventLink):
        page = FITCrawler.retrieveUrl(os.path.join(ROOT_PAGES_URL, eventLink), '    Event page %s' % eventId)
        replacementsDict = {}
        
        # replace links in this page
        page = self.replaceLinks(page, replacementsDict, 2)
        # save graph + subpages and replace its links
        page = self.handleGraphAndSubpages(page, courseDirname)
        # save this page
        FITCrawler.saveFile(os.path.join(courseDirname, 'event-%s.html' % eventId), page)
        
    #enddef
    
    
    def handleGraphAndSubpages (self, html, courseDirname, handleSubpages = False):
        '''
        Documentation
        '''
        linkMatch = GRAPH_IMAGE_RE.search(html)
        if linkMatch:
            link = linkMatch.group(1)
            graphId = linkMatch.group(2)
            # save image
            graphData = FITCrawler.retrieveUrl(os.path.join(ROOT_PAGES_URL, link), 'Graph file ')
            FITCrawler.saveFile(os.path.join(courseDirname, 'graph-'+graphId+'.png'), graphData, True)
            html = html.replace(link, 'graph-'+graphId+'.png')
        #endif
        
        if not handleSubpages:
            return html
        #endif
        
        # save course annotations page
        linkMatch = COURSE_ANNOTATIONS_RE.search(html)
        if linkMatch:
            link = linkMatch.group(1)
            # save page
            linkPage = FITCrawler.retrieveUrl(link, 'Annotations page ')
            linkPage = self.replaceLinks(linkPage, {}, 2)
            FITCrawler.saveFile(os.path.join(courseDirname, 'annotations.html'), linkPage)
            # replace links to this page
            html = html.replace(link, 'annotations.html')
        #endif
        
        # save course wiki page
        linkMatch = COURSE_WIKI_RE.search(html)
        if linkMatch:
            link = linkMatch.group(1)
            # save page
            linkPage = FITCrawler.retrieveUrl(os.path.join(ROOT_PAGES_URL, link), 'Wiki page ')
            linkPage = self.replaceLinks(linkPage, {}, 2)
            FITCrawler.saveFile(os.path.join(courseDirname, 'wiki.html'), linkPage)
            # replace links to this page
            html = html.replace(link, 'wiki.html')
        #endif   
        
        # return replaced src
        return html
    #enddef
    
    @staticmethod
    def retrieveUrl (url, urlName = ''):
        '''
        Documentation
        '''
        # replace &amp; => &
        url = url.replace('&amp;', '&')
        try:
            res = urllib2.urlopen(url)
        except urllib2.HTTPError, e:
            raise CrawlerException(urlName+'HTTPError = ' + str(e.code))
        except urllib2.URLError, e:
            raise CrawlerException(urlName+'URLError = ' + str(e.reason))
        except httplib.HTTPException, e:
            raise CrawlerException(urlName+'HTTPException')
        #endtry
        
        return res.read()
    #enddef
    
    @staticmethod
    def saveFile (path, data, binary = False):
        '''
        Documentation
        '''
        fullPath = os.path.join(ROOT_DIR_NAME, path)
        mode = 'w' if not binary else 'wb'
        try:
            f = open(fullPath, mode)
        except IOError:
            raise CrawlerException("Could not open file \"%s\" for write." % fullPath)
        #endtry
        try:
            f.write(data)
        except IOError:
            raise CrawlerException("Error while writing to the file \"%s\" for write." % fullPath)
        #endtry
        f.close()
    #enddef
    
    
    def replaceLinks (self, html, replacementsDict, directoryDepth):
        '''
        Documentation
        '''
        pathPrefix = '../' * directoryDepth
        
        # replace CSS and the common images
        for src, dst in self.RESOURCES.iteritems():
            html = html.replace('/'+src, os.path.join(pathPrefix, RESOURCES_DIR_NAME, dst))
        #endfor
        
        # replace with dict
        for src, dst in replacementsDict.iteritems():
            html = html.replace(src, dst)
        #endfor
        
        # add encoding info to the header
        html = html.replace('<head>', '<head>'+"\n"+'<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-2">')
        
        return html
    #enddef
    
    
    def saveResources (self):
        '''
        Documentation
        '''        
        FITCrawler.dbg('Saving web page resources - CSS and images...')
        # create directory
        try:
            os.mkdir(os.path.join(ROOT_DIR_NAME, RESOURCES_DIR_NAME))
        except OSError, e:
            pass # exists yet => OK
        #endtry
        for src, dst in self.RESOURCES_WIS.iteritems():
            data = FITCrawler.retrieveUrl(os.path.join(ROOT_URL, src), 'Resource from WIS ')
            FITCrawler.saveFile(os.path.join(RESOURCES_DIR_NAME, dst), data, True)
        #endfor
        for src, dst in self.RESOURCES_WEB.iteritems():
            data = FITCrawler.retrieveUrl(os.path.join(ROOT_WEB_URL, src), 'Resource from WEB ')
            # replace also image sources in web CSS file
            if src == 'common/style/style.css':
                data = data.replace('images/left_strip.png', 'left_strip.png')
                data = data.replace('images/right_strip.png', 'right_strip.png')
                data = data.replace('images/ninsignie_cs.jpg', 'ninsignie_cs.jpg')
            #endif
            FITCrawler.saveFile(os.path.join(RESOURCES_DIR_NAME, dst), data, True)
        #endfor
    #enddef
    
    
    @staticmethod
    def dbg (text):
        """Documentation"""        
        if DEBUG:
            print text
        #endif
    #enddef
    
#endclass

if __name__ == "__main__":
    crawler = FITCrawler()
    try:
        crawler.parseAndSave()
    except CrawlerException, e:
        print >> sys.stderr, "CrawlerException:\n" + e.message
    #endtry
#endif
