"""Gerrit reviewers adding tool.

Allow fast and easy adding reviewers to commit on gerrit host.

Usage:
    gar.py [-hv] [-k KEY] [-s HOST] [-p PORT] [-u USER] [-a ADDRS] CHANGE_ID

Options:
    -h --help                   show this help
    -v --version                show version
    -k KEY, --key KEY           set path to private key [default: ~/.ssh/id_rsa]
    -s HOST, --host HOST        set remote host address [default: review.openstack.org]
    -p PORT, --port PORT        set remote port [default: 29418]
    -u USER, --user USER        username which will connect to remote server [default is your username]
    -a ADDRS --addresses ADDRS  file with emails of reviewers to be added [default: ~/.gar/reviewers]

Arguments:
    CHANGE_ID  gerrit Change-Id number

"""
# TODO(sbog): add groups of users in file with addresses

from docopt import docopt
import os
import paramiko
import socket
import sys

if __name__ == '__main__':

    args = docopt(__doc__)
    print(args)
    sys.exit(0)

    keyp = '%s/.ssh/id_rsa' % os.environ['HOME']
    host = 'review.openstack.org'
    user = 'test' # test it against getpass.getuser later
    port = 29418
    comm = 'gerrit set-reviewers '
    addr = 'test@test.com' # get it from config
    chid = 226806 # get it from command line

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, key_filename=keyp, port=port)
    stdin, stdout, stderr = client.exec_command('gerrit set-reviewers -a %s 226776' % addr)
    data = stdout.read() + stderr.read()
    client.close()
