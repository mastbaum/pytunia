import os
import sys
import shutil
import uuid
import subprocess

# helper functions
def system(cmd, wd=None):
    '''a wrapper for subprocess.call, which executes cmd in working directory
    wd in a bash shell, returning the exit code.'''
    if wd:
        cmd = ('cd %s && ' % wd) + cmd
    print cmd
    return subprocess.call([cmd], executable='/bin/bash', shell=True)

def svn_co(url, target, username=None, password=None, wd=None):
    '''check out a revision from an svn server, optionally providing a
    username and password. the arguments are parsed as::

        cd [wd] && svn co [url] [target] --username=[username] \
    --password=[password]
    '''
    if wd:
        target = os.path.join(wd, target)
    target = os.path.abspath(target)
    if not os.path.exists(target):
        cmd = ' '.join(['svn co', url, target])
        if username: cmd = ' '.join([cmd, '--username=%s' % username])
        if password: cmd = ' '.join([cmd, '--password=%s' % password])
        return system(cmd)
    else:
        return None

# main task function
def execute(testname=None, svn_url=None, revnumber=None, svn_user=None, svn_pass=None, scons_options='-j6'):
    '''check out a revision with svn, build it with scons, and return back the
    build log.
    '''
    if testname is None:
        return {'success': False, 'reason': 'missing test name'}
    if not revnumber:
        return {'success': False, 'reason': 'missing revision number'}
    if not svn_url:
        return {'success': False, 'reason': 'missing svn url'}

    revnumber = str(revnumber)

    # temporary working directory
    wd = str(uuid.uuid4())
    os.mkdir(wd)

    # get the code
    ret = svn_co(svn_url, revnumber, username=svn_user, password=svn_pass, wd=wd)
    if ret is None or ret != 0:
        return {'success': False, 'reason': 'svn co failed'}
    wcpath = os.path.abspath(os.path.join(wd, revnumber))
    env_file = os.path.join(wcpath, 'env.sh')

    # build with scons
    results = {'success': True, 'attachments': []}
    system('./configure', wcpath)
    ret = system('source %s && scons %s' % (env_file, scons_options), wcpath)
    results['scons_returncode'] = ret
    if ret != 0:
        results['success'] = False
        results['reason'] = 'build failed'
    else:
        # run the requested rattest
        testpath = os.path.join(wcpath, 'test', 'full')
        ret = system('source %s && rattest -t %s' % (env_file, testname), testpath)
        if ret != 0:
            results['success'] = False
            results['reason'] = 'rattest failed'
        else:
            # attach results
            for root, dirs, files in os.walk(os.path.join(testpath,testname), topdown=False):
                for name in files:
                    fname = os.path.join(root, name)
                    with open(fname,'r') as f:
                        attachment = {'filename': fname, 'contents': f.read()}
                        if fname == 'results.html':
                            attachment['link_name'] = 'rattest Results'
                        results['attachments'].append(attachment)

    # delete the working directory
    shutil.rmtree(os.path.abspath(wd))

    return results

if __name__ == '__channelexec__':
    kwargs = channel.receive()
    results = execute(**kwargs)
    channel.send(results)

if __name__ == '__main__':
    print execute(testname=sys.argv[1], svn_url=sys.argv[2], revnumber=sys.argv[3])

