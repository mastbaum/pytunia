#/usr/bin/env python2.5

# tasks.py
#
# Definitions for pytunia tasks
#
# Andy Mastbaum (mastbaum@hep.upenn.edu), June 2011
#

import subprocess

debug = True

def system(cmd, wd=None):
    '''a wrapper for subprocess.call, which executes cmd in working directory
    wd in a bash shell, returning the exit code.'''
    if wd:
        cmd = ('cd %s && ' % wd) + cmd
    if debug:
        print cmd
        return 0
    return subprocess.call([cmd], executable='/bin/bash', shell=True)

class Test:
    '''hmm'''
    def __init__(self, name):
        self.name = name
        self.results = {}
    def execute(self):
        '''system calls to run this task. this should be overridden in
        subclasses of Task.'''
    def results_stringify(self):
        # need a map<string,string> for thrift
        results_str = {}
        for item in results:
            if type(results[item]) == file:
                results_str[str(item)] = results[item].read()
            else:
                results_str[str(item)] = str(results[item])
        return results_str

#task = Task('test')
#print task.name
#task.execute()

######
# vcs.py

class RepositoryExistsException(Exception):
    def __init__(self, target):
        self.target = target
    def __str__(self):
        return repr(self.target)

# wrap these in classes?
def svn_co(url, target, username=None, password=None):
    target = os.path.abspath(target)
    if not os.path.exists(target):
        cmd = ' '.join(['svn co', url, target])
        if username: cmd = ' '.join([cmd, '--username=%s' % username])
        if password: cmd = ' '.join([cmd, '--password=%s' % password])
        return system(cmd)
    else:
        raise RepositoryExistsException(target)

def git_clone(url, target):
    target = os.path.abspath(target)
    if not os.path.exists(target):
        cmd = ' '.join(['git clone', url, target])
        return system(cmd)
    else:
        raise RepositoryExistsException(target)

######

######
# builder.py

class AlreadyBuiltException(Exception):
    def __init__(self, target):
        self.target = target
    def __str__(self):
        return repr(self.target)

class BuildLockedException(Exception):
    def __init__(self, target):
        self.target = target
    def __str__(self):
        return repr(self.target)

# wrap these in classes?
def scons(build_dir, config_cmd=None, options=None, binary=None, clean=False):
    '''binary is binary target, which we can check for to see if it's built'''
    build_dir = os.path.abspath(build_dir)
    lock_file = os.path.join(build_dir, 'pytunia.lock')
    if not os.path.exists(lock_file):
        if clean:
            system(clean) # catch return value?
        if binary:
            binary_target = os.path.join(build_dir, binary)
            if not os.path.exists(binary_target):
                raise AlreadyBuiltException(build_dir)
        cd_cmd = ' '.join(['cd', build_dir])
        scons_cmd = ' '.join(['scons', options])
        cmd = ' && '.join([cd_cmd, config_cmd, scons_cmd])
        return system(cmd)
    else:
        raise BuildLockedException(build_dir)

######
# help.py

    class TarFailedException(Exception)
        def __init__(self, target):
            self.target = target
        def __str__(self):
            return repr(self.target)

    def rattest(wd, test_name):
        # factor all of this out
        if ret_code == 0:
            cd_cmd = ' '.join(['cd', wd])
            tar_cmd = ' '.join(['tar', 'czvf', output_name, test_name])
            cmd = ' && '.join([cd_cmd, tar_cmd])
            ret_code = system(cmd)
            if ret_code == 0:
                tarball_file = os.path.join(wd, output_name)
                return open(tarball_file)
            else:
                raise TarFailedException(output_name)
        else:
            raise TestFailedException(test_name)

import os

from site_specific import rat_svn_url

class RATTest(Test):
    '''hmmmmm'''
    class TestFailedException(Exception)
        def __init__(self, target):
            self.target = target
        def __str__(self):
            return repr(self.target)
    def execute(self, project=None, branch=None, wd='.'):
        rat_root = os.path.join(wd, self.rev_id)

        # svn checkout
        try:
            svn_co(rat_svn_url, rat_root, revnumber=self.rev_id)
        except RepositoryExistsException as e:
            print 'RATTest: repository already exists at', e.target

        # scons build
        try:
            scons(rat_root,
                  config_cmd = './configure && source ./env.sh'
                  options = '-j2',
                  binary='bin/rat_%s' % os.environ['G4SYSTEM'])
        except BuildLockedException as e:
            print 'RATTest: Repository at', e.target, 'locked. A build is probably in progress.'
        except AlreadyBuiltException as e:
            print 'RATTest: Repository at', e.target, 'already built'

        # rattest
        test_dir = os.path.join(rat_root, 'test/full')
        success = True

        cd_cmd = ' '.join(['cd', test_dir])
        rattest_cmd = ' '.join(['rattest', test_name])
        cmd = ' &&  '.join([cd_cmd, rattest_cmd])
        ret_code = system(cmd)

        if ret_code == 0:
            try:
                results['payload'] = pack('test_dir ' + self.name)
                results['additional_links': 'results.html'] # too kludgy?
            except PackFailed as e:
                print 'RATTest: failed to create archive of ', self.name
        else:
            raise TestFailedException(test_name)


#acrylic_attenuation = RATTest('acrylic_attenuation')
#acrylic_attenuation.execute()

#class CxxTest(Test):


#class StaticTest(Test):


#acrylic_attenuation = RATTest


#pseudocode:

#def rattest:
#    if exists(base_dir + rev_id)
#        cd
#        if built:
#            cd + test/full && rattest this.__name__
#        else:
#            place lockfile
#            cd && configure && source && scons > log_file

#acrylic_attenuation = rattest()

#def cppcheck:

