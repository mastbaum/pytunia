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
    return subprocess.call([cmd], executable='/bin/bash', shell=True)

def git_clone(url, sha, target, wd=None):
    '''clone a git repository. the arguments are parsed as::

        cd [wd] && git clone [url] [target] && git checkout [sha]

    you may need to set up ssh keys if authentication is needed.
    '''
    if wd:
        target = os.path.join(wd, target)
    target = os.path.abspath(target)
    if not os.path.exists(target):
        cmd = ' '.join(['git clone', url, target, '&& cd %s && ' % target, 'git checkout', sha, '&> /dev/null'])
        return system(cmd)
    else:
        return None

# main task function
def execute(testname=None, git_url=None, sha=None, scons_options='-j2'):
    '''clone a git repository, build it with scons, and return back the
    rattest result files.
    '''
    if testname is None:
        return {'success': False, 'reason': 'missing test name'}
    if not sha:
        return {'success': False, 'reason': 'missing revision id'}
    if not git_url:
        return {'success': False, 'reason': 'missing git url'}

    # temporary working directory
    wd = str(uuid.uuid4())
    os.mkdir(wd)

    # get the code
    ret = git_clone(git_url, sha, sha, wd=wd)
    if ret is None or ret != 0:
        return {'success': False, 'reason': 'git clone failed'}

    wcpath = os.path.abspath(os.path.join(wd, sha))

    # build with scons
    results = {'success': True, 'attachments': []}
    system('./configure', wcpath)
    env_file = os.path.join(wcpath, 'env.sh')
    ret = system('source %s && scons %s &> build_log.txt' % (env_file, scons_options), wcpath)
    results['scons_returncode'] = ret
    if ret != 0:
        results['success'] = False
        results['reason'] = 'build failed'
    else:
        # run the requested rattest
        testpath = os.path.join(wcpath, 'test', 'full')
        ret = system('source %s && rattest -t %s &> /dev/null' % (env_file, testname), testpath)
        if ret != 0:
            results['success'] = False
            results['reason'] = 'rattest failed'

        # attach results
        for root, dirs, files in os.walk(os.path.join(testpath,testname), topdown=False):
            for name in files:
                fname = os.path.join(root, name)
                basename = os.path.basename(fname)
                with open(fname,'r') as f:
                    attachment = {'filename': basename, 'contents': f.read()}
                    if basename == 'results.html':
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
    print execute(testname=sys.argv[1], git_url=sys.argv[2], sha=sys.argv[3])

