# core classes and stuff

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

def system(cmd, wd=None):
    '''a wrapper for subprocess.call, which executes cmd in working directory
    wd in a bash shell, returning the exit code.'''
    if wd:
        cmd = ('cd %s && ' % wd) + cmd
    if debug:
        print cmd
        return 0
    return subprocess.call([cmd], executable='/bin/bash', shell=True)

class TarFailedException(Exception)
    def __init__(self, target):
        self.target = target
    def __str__(self):
        return repr(self.target)

