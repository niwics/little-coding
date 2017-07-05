#!/usr/bin/python

import argparse
import logging
import os
import gio
import gtk


def process_dir(path):
    for subdir, dirs, files in os.walk(path):
        for file in files:
            filepath = os.path.join(subdir, file)

            f = gio.File(path=filepath)
            info = f.query_info('*')

            # We check if there's a thumbnail for our file
            preview = info.get_attribute_byte_string ("thumbnail::path")

            image = None
            if preview:
                image = gtk.image_new_from_file (preview)
            else:
                # If there's no thumbnail, we check get_icon, who checks the
                # file's mimetype, and returns the correct stock icon.
                icon = info.get_icon()
                image = gtk.image_new_from_gicon (icon, gtk.ICON_SIZE_MENU)

            print subdir

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('directory', help='Path to the directory')
    parser.add_argument('--verbose', help='Verbose mode', action='store_true')
    opts = vars(parser.parse_args())

    # logger names can be hierarchically set
    log = logging.getLogger(__name__)
    log.setLevel("DEBUG" if opts["verbose"] else "INFO")
    # create console handler
    ch = logging.StreamHandler()
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s: %(message)s', '%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    log.addHandler(ch)

    process_dir(opts['directory'])


if __name__ == "__main__":
    main()
