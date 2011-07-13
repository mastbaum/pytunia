#/usr/bin/env python2.5

# tasks.py
#
# Definitions for pytunia tasks
#
# Andy Mastbaum (mastbaum@hep.upenn.edu), June 2011
#

import subprocess
import os
from site_specific import rat_svn_url

debug = True

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

