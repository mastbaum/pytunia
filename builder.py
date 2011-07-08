# build systems

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

