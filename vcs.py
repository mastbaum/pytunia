# version control systems

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

