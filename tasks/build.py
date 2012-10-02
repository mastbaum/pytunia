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

def git_clone(url, sha, target=None, wd=None):
    '''clone a git repository. the arguments are parsed as::

        cd [wd] && git clone [url] [target] && git checkout [sha]

    you may need to set up ssh keys if authentication is needed.
    '''
    if target is None:
        target = sha
    if wd:
        target = os.path.join(wd, target)
    target = os.path.abspath(target)
    if not os.path.exists(target):
        cmd = ' '.join(['git clone', url, target, '&& cd %s && ' % target, 'git checkout', sha, '&> /dev/null'])
        return system(cmd)
    else:
        return None

def git_merge(url, ref, wd=None):
    '''Merge ref sha from a remote at url into the repo at wd'''
    cmd = ' '.join(['git remote add fork', url])
    system(cmd, wd)

    cmd = ' '.join(['git pull fork', ref, '&> /dev/null'])
    return system(cmd, wd)

# main task function
def execute(git_url=None, sha=None, base_repo_url=None, base_repo_ref=None, scons_options='-j1'):
    '''check out a revision with git, build it with scons, and return back the
    build log.
    '''
    if not sha:
        return {'success': False, 'reason': 'missing revision id'}
    if not git_url:
        return {'success': False, 'reason': 'missing git url'}

    if base_repo_url and not base_repo_ref or base_repo_ref and not base_repo_url:
        return {'success': False, 'reason': 'incomplete base repository specification for merge'}

    # temporary working directory
    wd = str(uuid.uuid4())
    os.mkdir(wd)

    # get the code
    ret = git_clone(git_url, sha, wd=wd)
    if ret is None or ret != 0:
        shutil.rmtree(os.path.abspath(wd))
        return {'success': False, 'reason': 'git clone failed', 'code': str(ret)}

    wcpath = os.path.abspath(os.path.join(wd, sha))

    if base_repo_url is not None:
        ret = git_merge(base_repo_url, base_repo_ref, wcpath)
        if ret is None or ret != 0:
            shutil.rmtree(os.path.abspath(wd))
            return {'success': False, 'reason': 'git merge failed', 'code': str(ret)}

    # build with scons
    results = {'success': True, 'attachments': []}
    system('./configure', wcpath)
    env_file = os.path.join(wcpath, 'env.sh')
    if not os.path.exists(env_file):
        shutil.rmtree(os.path.abspath(wd))
        return {'success': False, 'reason': 'configure failed'}
    ret = system('source %s && scons %s &> build_log.txt' % (env_file, scons_options), wcpath)
    results['scons_returncode'] = ret
    if ret != 0:
        results['success'] = False
        results['reason'] = 'build failed'

    # attach log to results
    attachment = {}
    with open('%s/build_log.txt' % wcpath, 'r') as f:
        attachment = {'filename': 'build_log.txt', 'contents': f.read(), 'link_name': 'Build Log'}

    results['attachments'].append(attachment)

    # delete the working directory
    shutil.rmtree(os.path.abspath(wd))

    return results

if __name__ == '__channelexec__':
    kwargs = channel.receive()
    results = execute(**kwargs)
    channel.send(results)

if __name__ == '__main__':
    if len(sys.argv) > 3:
        base_repo_url = sys.argv[3]
        base_repo_ref = sys.argv[4]
    else:
        base_repo_url = None
        base_repo_ref = None

    print execute(git_url=sys.argv[1], sha=sys.argv[2], base_repo_url=base_repo_url, base_repo_ref=base_repo_ref)

