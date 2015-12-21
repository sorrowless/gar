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
    --project PROJECT     gerrit project which consist a commit [default: openstack/fuel-library]
    -a --addresses ADDRS  file with emails of reviewers to be added [default: ~/.gar/reviewers]

Arguments:
    CHANGE_ID  gerrit Change-Id number

"""
# TODO(sbog): add groups of users in file with addresses

import json
from docopt import docopt
from getpass import getuser
import logging
import os
import paramiko
import socket
import sys
import traceback

class Options():
    def __init__(self):
        """ Initialize main variables.
        self.args     - store command line arguments
        self.options  - store options hash
        self.logger   - store logging instance
        self.conffile - store gar config file
        """
        self.args = {}
        self.options = {}
        self.logger = False
        self.conffile = {}
        # Read command line options and set logging in constructor
        self._readOptions()
        # Read config file
        self._readConfig()
        if self.conffile:
            self._optionsMerge()
        else:
            self.options = self.args
        # We should place default username if there are no user set by options
        # Be aware, self.args is a Hash, it means that it is one object with
        # self.options
        if not self.args['--user']:
            self.args['--user'] = getuser()
        self.logger.info('End options is: ' + str(self.options))


    def _readOptions(self):
        """ Reads command line options and saves it to self.args hash. Also set
        log level and logging message format
        """
        self.args = docopt(__doc__, version='0.2')
        # Set logging level. Log level in python logging lowers to 10 points
        # with each level, so we set it to 10 (maximum) in case of '-v'>5 and
        # higher it for less '-v's
        loglevel = (5 - self.args['-v'])*10 if self.args['-v'] < 5 else 10
        logging.basicConfig(level = loglevel,
                format='%(asctime)s %(name)-30s %(levelname)-9s %(message)s')
        self.logger = logging.getLogger('gar.main')
        self.logger.debug('Passed arguments is: ' + str(self.args))


    def _readConfig(self):
        """ Reads config file and saves values from it to self.conffile hash.
        """
        try:
            with open(os.path.expanduser('~/.gar/config'), 'r') as f:
                self.conffile = json.loads(f)
        except IOError:
            self.logger.info("Config file not found. Only command-line options will be used")

    def _optionsMerge(self):
        """ Returns merged dictionary for options from command line and options
        from config file. Command line arguments will have preference over
        config directives.
        """
        self.logger.debug("start options merge")
        self.options = dict((str(key), args.get(key) or self.conffile.get(key)) for key in
                            set(self.args) | set(self.conffile))


class Gar():
    def __init__(self, options, logger):
        self.options = options
        self.logger = logger
        self.pkeypassword = ''
        self.addrs = ''
        self.client = False

    def readPrivateKeyPassword(self):
        """ Read private key password from options
        """
        self.logger.debug("read private key password")
        if self.options['--keypass']: self.pkeypassword = self.options['--keypass']
        elif self.options['--passfile']:
            try:
                with open(self.options['--passfile']) as f:
                    self.pkeypassword = f.read()
            except FileNotFoundError:
                self.logger.critical("Sorry, file with credentials was not found, exiting..")
                self.logger.debug(traceback.format_exc())
                sys.exit(1)


    def loadReviewers(self):
        """ Load reviewers list from file
        """
        self.logger.debug("load reviewers list")
        try:
            with open(os.path.expanduser(self.options['--addresses']), 'r') as f:
               self.addrs = [line.rstrip() for line in f.readlines()]
        except FileNotFoundError:
            self.logger.critical("Sorry, file with reviewers was not found, exiting...")
            self.logger.debug(traceback.format_exc())
            sys.exit(1)


    def connect(self):
        """ Connects to server
        """
        self.logger.debug("connect")
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Load private key
        if self.pkeypassword:
            try:
                self.client.connect(hostname=self.options['--host'],
                               username=self.options['--user'],
                               key_filename=os.path.expanduser(self.options['--key']),
                               password=self.pkeypassword,
                               port=int(self.options['--port']))
            except paramiko.ssh_exception.SSHException:
                self.logger.critical('Unable to parse you private key. Maybe wrong password or user? Exiting...')
                self.logger.debug(traceback.format_exc())
                sys.exit(1)
        else:
            try:
                self.client.connect(hostname=self.options['--host'],
                               username=self.options['--user'],
                               key_filename=os.path.expanduser(self.options['--key']),
                               port=int(self.options['--port']))
            except paramiko.ssh_exception.PasswordRequiredException:
                self.logger.critical('Auth with provided credentials failed. Private key is encrypted?')
                self.logger.debug(traceback.format_exc())
                sys.exit(1)
            except paramiko.ssh_exception.AuthenticationException:
                self.logger.critical('Auth with provided credentials failed. User differs from "{user}"? Exiting...'.format(user=self.options['--user']))
                self.logger.debug(traceback.format_exc())
                sys.exit(1)



    def addReviewers(self):
        self.logger.debug("add reviewers to change")
        stdin, stdout, stderr = self.client.exec_command('gerrit set-reviewers -p %s -a %s %s'
                                  % (self.options['--project'], ' -a '.join(self.addrs), self.options['CHANGE_ID']))
        errs = stderr.read()
        out = stdout.read()
        self.logger.error(errs) if errs else errs
        self.logger.info(out) if out else out
        self.logger.info("End adding reviewers to change")


def main():
    o = Options()
    c = Gar(o.options, o.logger)
    c.readPrivateKeyPassword()
    c.loadReviewers()
    c.connect()
    c.addReviewers()
    c.client.close()

if __name__ == '__main__':
    main()

