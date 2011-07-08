#!/usr/bin/env python2.5

# tasks.py
#
# Definitions for pytunia tasks
#
# Andy Mastbaum (mastbaum@hep.upenn.edu), June 2011
#

class Task:
    '''hmm'''
    def __init__(self):
        pass


class RATTest(Test):
    '''hmmmmm'''
    pass

#acrylic_attenuation = RATTest


pseudocode:

def rattest:
    if exists(base_dir + rev_id)
        cd
        if built:
            cd + test/full && rattest this.__name__
        else:
            place lockfile
            cd && configure && source && scons > log_file

acrylic_attenuation = rattest()

def cppcheck:

    



