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

def execute(git_url=None, sha=None, base_repo_url=None, base_repo_ref=None):
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
        return {'success': False, 'reason': 'git clone failed'}

    wcpath = os.path.abspath(os.path.join(wd, sha))

    if base_repo_url is not None:
        ret = git_merge(base_repo_url, base_repo_ref, wcpath)
        if ret is None or ret != 0:
            shutil.rmtree(os.path.abspath(wd))
            return {'success': False, 'reason': 'git merge failed', 'code': str(ret)}

    # find instances of fixme
    results = {'success': True, 'attachments': []}
    ret = system('grep -irn --exclude=fixme.txt --exclude=*.git --exclude=*.svn fixme . &> fixme.txt', wcpath)
    results['grep_returncode'] = ret

    # parse grep output into formatted html page
    with open(os.path.join(wcpath,'fixme.html'),'w') as fo:
        fo.write('<html>\n<head>\n<title>FIXME Detector</title>\n</head>\n')
        fo.write('<body>\n<h1>Instances of "fixme" in source tree</h1>\n')
        fo.write('<table border>\n<tr>\n<th>File</th>\n<th>Line</th>\n')
        fo.write('<th>Code</th>\n<th>Last Edited</th>\n</tr>')
        with open(os.path.join(wcpath,'fixme.txt'),'r') as fi:
            for item in fi.readlines():
                fname, line, code = [x.lstrip() for x in item.split(':', 2)]
                fo.write('<tr>\n<td>%s</td>\n<td>%s</td>\n<td>%s</td>\n' % (fname, line, code))

                cmd = subprocess.Popen(['git', 'blame', '-p', '-L', '%s,%s' % (line, line), fname], stdout=subprocess.PIPE, cwd=wcpath)
                blame = cmd.communicate()[0].splitlines()
                last_rev = blame[0].split()[0]
                last_author = ' '.join(blame[1].split()[1:])
                fo.write('<td>%s, %s</td>\n</tr>\n' % (last_author, last_rev))

        fo.write('</table>\n</body>\n</html>')

    # attach html to results
    attachment = {}
    with open(os.path.join(wcpath,'fixme.html'), 'r') as f:
        attachment = {'filename': 'fixme.html', 'contents': f.read(), 'link_name': 'FIXMEs'}

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

