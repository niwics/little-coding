import argparse
import logging
import os
import PTN
import re
import shutil
import sys

logger = logging.getLogger("video-rename")
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s {%(name)s: %(lineno)s}')
ch.setFormatter(formatter)
logger.addHandler(ch)

parser = argparse.ArgumentParser(description='Rename the video', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('path', help='Path to process')
parser.add_argument('--dry-run', '-d', help='Dry run', action='store_true')
parser.add_argument('--verbose', '-v', help='Verbose output', action='store_true', default=False)
args = parser.parse_args()

dry_run = args.dry_run
logger.setLevel("DEBUG" if args.verbose else "INFO")
basename = os.path.basename(args.path)

# check whether the name is correct yet
if re.match(r".+ d\(\d{4}\)\.\w+$", basename):
    logger.debug("Name OK: \"{}\"".format(basename))
    sys.exit()

info = PTN.parse(basename)

logger.debug("Parsed by PTN: {}".format(info))

# remove dummy words from the title
title = re.sub(r" HD$", r"", info["title"])

new_name = title
year = 0
if not ("year" in info):
    print("Year not found - fill it:")
    year_line = input()
    year = year_line.strip()
    try:
        year = int(year)
    except ValueError as e:
        print("Invalid year value")
        sys.exit()
    if year < 30:
        year = 2000+year
    elif year >= 30 and year < 100:
        year = 1900+year
else:
    year = info["year"]
if not ("group" in info):
    print("Extension not detected!")
    sys.exit()
new_name += " ({}).{}".format(year, info["group"])

print("{} -- Rename to this name? Enter to proceed or writhe the new variant to use it:".format(new_name))
input_line = input()

if input_line != "":
    if input_line == "s":
        sys.exit()
    new_name = input_line.strip()

# rename
new_filename = os.path.join(os.path.dirname(args.path), new_name)
if not dry_run:
    shutil.move(args.path, new_filename)

print("{} \"{}\" -> \"{}\"".format("Would rename" if dry_run else "Renamed", args.path, new_filename))
