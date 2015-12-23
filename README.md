Gar
===
[![Build Status](https://travis-ci.org/sorrowless/gar.svg?branch=master)](https://travis-ci.org/sorrowless/gar)

Description
-----------
Gar is acronym for 'Gerrit add Reviewers'. It is simple wrapper arounf
standard gerrit add-reviewers tool to conveniently adding group of users.


Installation
------------
To install gar from PyPI, simply run

``$ pip install batticon``

It will download and install it with all requirements.


Usage
-----
To use gar, simply run

``$ gar <Chande-Id>``

with needed options to add some reviewers to your change-id. This tool was
created for me personally, so I suppose that you will need to override defaults.
To better understand which options you can use, run gar with '-h' flag.


Settings
--------
Settings file named *config* and used standard JSON markup.
Today it have next settings:

* "--key": <set path to private key [default: ~/.ssh/id_rsa]>
* "--keypass": <private key password if it exist>
* "--passfile": <file with password for private key if you don't want to store
  password to your private key in config file>
* "--host": <set remote host address [default: review.openstack.org]>
* "--port": <set remote port [default: 29418]>
* "--user": <username which will connect to remote server [default is your
  username]>
* "--project": <gerrit project which consist a commit [default:
  openstack/fuel-library]>
* "--addresses": <file with emails of reviewers to be added [default:
  ~/.gar/reviewers]>

Settings file should be placed in:

* ~/.gar/config

Program also supposed to have ability to read file with reviewers addresses
that should be added as reviewers to desired patchset. This file should
contain reviewers addresses, one per line.


Your app doesn't work!!
-----------------------
Just write to me, don't be shy. I will really glad to help you with your
problem.



