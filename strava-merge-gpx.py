# @author: niwics, niwi.cz, August 2018
# Simple single-purpose tool for merging two Strava workouts - first with HR, second without HR

import gpxpy
import gpxpy.gpx
from gpxpy import gpxfield as mod_gpxfield
import datetime

# input files
gpx_file1 = open('/Users/miroslav.kvasnica/Downloads/Morning_Run.gpx', 'r')
gpx_file2 = open('/Users/miroslav.kvasnica/Downloads/Morning_Run(1).gpx', 'r')
# output file
gpx_file_out = open('/Users/miroslav.kvasnica/Downloads/merged.gpx', 'w')
# datetime of existing HR element, which HR value will be used in missing records
fake_hr_time = datetime.datetime(2018, 8, 18, 4, 25, 41)

gpx1 = gpxpy.parse(gpx_file1)
gpx2 = gpxpy.parse(gpx_file2)

out_gpx = gpxpy.gpx.GPX()
out_track = gpxpy.gpx.GPXTrack()
out_gpx.tracks.append(out_track)
out_segment = gpxpy.gpx.GPXTrackSegment()
out_track.segments.append(out_segment)

reference_extension = None
for gpx_set in (gpx1, gpx2):
    i = 1
    for track in gpx_set.tracks:
        for segment in track.segments:
            for point in segment.points:
                if point.time == fake_hr_time:
                    reference_extension = point.extensions[0]
                if gpx_set == gpx2 and reference_extension:
                    point.extensions = [reference_extension]
                out_segment.points.append(point)
                i += 1

gpx_file_out.write(out_gpx.to_xml())
#print 'Created GPX:', out_gpx.to_xml()

# Necessary postprocessings for importing to Strava:
#   1. Copy header from first file
#   2. Replace HR elements in the merged file using vim: `:%s/http:\/\/www.garmin.com\/xmlschemas\/TrackPointExtension\/v1/gpxtpx/g`