#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#  Copyright (C) 2014 EDF SA                                                 #
#                                                                            #
#  This file is part of Clara                                                #
#                                                                            #
#  This software is governed by the CeCILL-C license under French law and    #
#  abiding by the rules of distribution of free software. You can use,       #
#  modify and/ or redistribute the software under the terms of the CeCILL-C  #
#  license as circulated by CEA, CNRS and INRIA at the following URL         #
#  "http://www.cecill.info".                                                 #
#                                                                            #
#  As a counterpart to the access to the source code and rights to copy,     #
#  modify and redistribute granted by the license, users are provided only   #
#  with a limited warranty and the software's author, the holder of the      #
#  economic rights, and the successive licensors have only limited           #
#  liability.                                                                #
#                                                                            #
#  In this respect, the user's attention is drawn to the risks associated    #
#  with loading, using, modifying and/or developing or reproducing the       #
#  software by the user in light of its specific status of free software,    #
#  that may mean that it is complicated to manipulate, and that also         #
#  therefore means that it is reserved for developers and experienced        #
#  professionals having in-depth computer knowledge. Users are therefore     #
#  encouraged to load and test the software's suitability as regards their   #
#  requirements in conditions enabling the security of their systems and/or  #
#  data to be ensured and, more generally, to use and operate it in the      #
#  same conditions as regards security.                                      #
#                                                                            #
#  The fact that you are presently reading this means that you have had      #
#  knowledge of the CeCILL-C license and that you accept its terms.          #
#                                                                            #
##############################################################################
"""
Interact with encrypted files using configurable methods

Usage:
    clara enc show <file>
    clara enc edit <file>
    clara enc encode <file>
    clara enc decode <file>
    clara enc -h | --help | help
"""

import os
import shutil
import subprocess
import sys
import tempfile

import docopt

from clara.utils import get_from_config, value_from_file


# In the future, this function will get the key using several method,
# right now, we only have one method and we'll use that one
def get_encryption_key():

    master_passwd_file = get_from_config("common", "master_passwd_file")

    if os.path.isfile(master_passwd_file):
        password = value_from_file(master_passwd_file, "ASUPASSWD")
        if len(password) > 20:
            return password
        else:
            sys.exit('There was some problem reading the value of ASUPASSWD')
    else:
        sys.exit('Unable to read: {0}'.format(master_passwd_file))


def do(op, origfile):
    password = get_encryption_key()
    f = tempfile.NamedTemporaryFile()

    if op == "decrypt":
        cmd = ['openssl', 'aes-256-cbc', '-d', '-in', origfile, '-out', f.name, '-k', password]
    elif op == "encrypt":
        cmd = ['openssl', 'aes-256-cbc', '-in', origfile, '-out', f.name, '-k', password]

    retcode = subprocess.call(cmd)

    if retcode != 0:
        f.close()
        sys.exit('CLARA: command failed {0}'.format(" ".join(cmd)))
    else:
        return f


def main():
    dargs = docopt.docopt(__doc__)

    if dargs['show'] or dargs['edit'] or dargs['decode']:
        if not dargs['<file>'].endswith(".enc"):
            sys.exit("The filename doesn't end with .enc - {0}. All encrypted files must have the suffix '.enc'")

    if dargs['encode']:
        if dargs['<file>'].endswith(".enc"):
            sys.exit("The filename ends with .enc - {0}. This file is probably already encrypted.")

    if dargs['show']:
        f = do("decrypt", dargs['<file>'])
        subprocess.call(['sensible-pager', f.name])
        f.close()
    elif dargs['edit']:
        pass  # TODO
    elif dargs['encode']:
        f = do("encrypt", dargs['<file>'])
        shutil.copy(f.name, dargs['<file>'] + ".enc")
        f.close()
    elif dargs['decode']:
        f = do("decrypt", dargs['<file>'])

        if dargs['<file>'].endswith(".enc"):
            shutil.copy(f.name, dargs['<file>'][0:-4])
        f.close()


if __name__ == '__main__':
    main()