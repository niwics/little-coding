#!/usr/bin/python

import argparse
import logging
import os
import subprocess
import time


DEFAULT_HOSTNAME = "8.8.8.8"
DEFAULT_SLEEP_SECONDS = 5


def ping(ip):
    cmd_list = ['ping', '-c', '1', '-W', str(1000*int(DEFAULT_SLEEP_SECONDS/2)), ip]
    # for OS X:
    #cmd_list = ['ping', '-c', '1', ip]
    log = logging.getLogger(__name__)
    log.debug(" ".join(cmd_list))
    with open(os.devnull, 'wb') as devnull:
        try:
            subprocess.check_call(cmd_list, stdout=devnull, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            log.debug(e) # debug => for verbose mode only
            return False
    return True


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('gateway', help='Internet gateway IP (local router)')
    parser.add_argument('--target',
                        help='Server name or IP to ping (default: %s)'% DEFAULT_HOSTNAME,
                        default=DEFAULT_HOSTNAME)
    parser.add_argument('--sleep',
                        help='Number of seconds to sleep (default: %s)'%DEFAULT_SLEEP_SECONDS,
                        default=DEFAULT_SLEEP_SECONDS)
    parser.add_argument('--verbose', help='Verbose mode', action='store_true')
    opts = vars(parser.parse_args())

    # logger names can be hierarchically set
    log = logging.getLogger(__name__)
    log.setLevel("DEBUG" if opts["verbose"] else "INFO")
    # create console handler
    ch = logging.StreamHandler()
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s: %(message)s',
                                  '%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    log.addHandler(ch)

    while True:
        response = ping(opts['target'])
        if response:
            log.info("OK")
        else:
            # test gateway accessibility
            response_gw = ping(opts['gateway'])
            if response_gw:
                log.error('NO_CONNECTION_TARGET: Could not connect to the remote server "%s".', opts['target'])
            else:
                log.error('NO_CONNECTION_GATEWAY: Could not connect to the gateway "%s".', opts['gateway'])
        time.sleep(DEFAULT_SLEEP_SECONDS)


if __name__ == "__main__":
    main()
