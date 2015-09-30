#!/usr/bin/env python
"""Gerrit reviewers adding tool.

Allow fast and easy adding reviewers to commit on gerrit host.

Usage:
    gar.py [-v...] [-k KEY] [--keypass KEYPASS | --passfile PASSFILE] [-s HOST] [-p PORT] [-u USER] [-a ADDRS] [--project PROJECT] CHANGE_ID
    gar.py -h
    gar.py --version

Options:
    -v                    verbosity level. Use more than one time to raise level (like -vvvv)
    -h --help             show this help
    --version             show version
    -k --key KEY          set path to private key [default: ~/.ssh/id_rsa]
    --keypass KEYPASS     private key password if it exist
    --passfile PASSFILE   file with password for private key
    -s --host HOST        set remote host address [default: review.openstack.org]
    -p --port PORT        set remote port [default: 29418]
    -u --user USER        username which will connect to remote server [default is your username]
    --project PROJECT     gerrit project which consist a commit [default: stackforge/fuel-library]
    -a --addresses ADDRS  file with emails of reviewers to be added [default: ~/.gar/reviewers]

Arguments:
    CHANGE_ID  gerrit Change-Id number

"""
# TODO(sbog): add groups of users in file with addresses

import configparser
from docopt import docopt
import getpass
import logging
import os
import paramiko
import socket
import sys
import traceback

if __name__ == '__main__':

    args = docopt(__doc__, version='0.2')
    loglevel = (5 - args['-v'])*10 if args['-v'] < 5 else 10
    logging.basicConfig(level = loglevel,
                        format='%(asctime)s %(name)-14s %(levelname)-9s %(message)s')
    logger = logging.getLogger('gar.main')
    logger.info(args)

    comm = 'gerrit set-reviewers '
    pkpass = ''

    # Try to read config file. Command line arguments will have
    # preference over config directives
    try:
        with open(os.path.expanduser('~/.gar/config') as f:
            conffile = configparser.ConfigParser()
            conffile.read(f)
    except FileNotFoundError:
        conffile = []

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Try to load password for private key
    if args['--keypass']: pkpass = args['--keypass']
    elif args['--passfile']:
        try:
            with open(args['--passfile']) as f:
                pkpass = f.read()
        except FileNotFoundError:
            logger.critical("Sorry, file with credentials was not found, exiting..")
            logger.debug(traceback.format_exc())
            sys.exit(1)

    # We will set some configuration directives prior to use them, cause there
    # are several places where we could get configs
    # TODO(sbog): implement config file merge

    # Load private key
    if pkpass:
        try:
            client.connect(hostname=args['--host'],
                           username=args['--user'],
                           key_filename=os.path.expanduser(args['--key']),
                           password=pkpass,
                           port=int(args['--port']))
        except paramiko.ssh_exception.SSHException:
            logger.critical('Unable to parse you private key. Maybe wrong password or user? Exiting...')
            logger.debug(traceback.format_exc())
            sys.exit(1)
    else:
        try:
            client.connect(hostname=args['--host'],
                           username=args['--user'],
                           key_filename=os.path.expanduser(args['--key']),
                           port=int(args['--port']))
        except paramiko.ssh_exception.PasswordRequiredException:
            logger.critical('Auth failed. Exiting...')
            logger.debug(traceback.format_exc())
            sys.exit(1)


    # Load reviewers from addresses file
    try:
        with open(os.path.expanduser(args['--addresses']), 'r') as f:
           addrs = [line.rstrip() for line in f.readlines()]
    except FileNotFoundError:
        logger.critical("Sorry, file with reviewers was not found, exiting...")
        logger.debug(traceback.format_exc())
        sys.exit(1)

    stdin, stdout, stderr = client.exec_command('gerrit set-reviewers -p %s -a %s %s'
                              % (args['--project'], ' -a '.join(addrs), args['CHANGE_ID']))
    errs = stderr.read()
    out = stdout.read()
    logger.error(errs) if errs else errs
    logger.info(out) if out else out
    client.close()
