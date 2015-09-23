"""Gerrit reviewers adding tool.

Allow fast and easy adding reviewers to commit on gerrit host.

Usage:
    gar.py [-hv] [-k KEY] [--keypass KEYPASS] [-s HOST] [-p PORT] [-u USER] [-a ADDRS] [--project PROJECT] CHANGE_ID

Options:
    -h --help             show this help
    -v --version          show version
    -k --key KEY          set path to private key [default: ~/.ssh/id_rsa]
    --keypass KEYPASS     private key password if it exist
    -s --host HOST        set remote host address [default: review.openstack.org]
    -p --port PORT        set remote port [default: 29418]
    -u --user USER        username which will connect to remote server [default is your username]
    --project PROJECT     gerrit project which consist a commit [default: stackforge/fuel-library]
    -a --addresses ADDRS  file with emails of reviewers to be added [default: ~/.gar/reviewers]

Arguments:
    CHANGE_ID  gerrit Change-Id number

"""
# TODO(sbog): add groups of users in file with addresses
# TODO(sbog): add logger, catch ssh return answer properly
# TODO(sbog): add keyfile with credentials for private key

from docopt import docopt
import os
import paramiko
import socket
import sys

if __name__ == '__main__':

    args = docopt(__doc__, version='0.1')
    print(args)

    comm = 'gerrit set-reviewers '
    addrs = ''

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Load private key
    if args['--keypass']:
        try:
            client.connect(hostname=args['--host'],
                           username=args['--user'],
                           key_filename=os.path.expanduser(args['--key']),
                           password=args['--keypass'],
                           port=int(args['--port']))
        except paramiko.ssh_exception.SSHException:
            print('Unable to parse you private key. Maybe wrong password or '
                  'user? Exiting...')
            sys.exit(1)
    else:
        try:
            client.connect(hostname=args['--host'],
                           username=args['--user'],
                           key_filename=os.path.expanduser(args['--key']),
                           port=int(args['--port']))
        except paramiko.ssh_exception.PasswordRequiredException:
            print('Your private key require a password and you did not point '
                  'it. Exiting...')
            sys.exit(1)


    # Load reviewers from addresses file
    try:
        with open(args['--addresses'], 'r') as f:
           addrs = [line.rstrip() for line in f.readlines()]
    except FileNotFoundError:
        print("Sorry, file with reviewers was not found, exiting...")
        sys.exit(1)

    stdin, stdout, stderr = client.exec_command('gerrit set-reviewers -p %s -a %s %s'
                              % (args['--project'], ' -a '.join(addrs), args['CHANGE_ID']))
    data = stdout.read() + stderr.read()
    client.close()
