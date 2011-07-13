#!/usr/bin/env python2.5

# leftovers

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

    
    # wtf?
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



