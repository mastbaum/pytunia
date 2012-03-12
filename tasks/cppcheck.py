import os
import sys
import shutil
import uuid
import subprocess
from xml.etree.ElementTree import ElementTree

# non-'error' IDs considered really bad in cppcheck. errors are always critical.
cppcheck_critical = ['unreadVariable','unusedFunction']

# cppcheck IDs highlighted in the output, but not considered failure-worthy
cppcheck_warn = ['stlSize','passedByValue','invalidscanf','unusedVariable']

def system(cmd, wd=None):
    '''a wrapper for subprocess.call, which executes cmd in working directory
    wd in a bash shell, returning the exit code.'''
    if wd:
        cmd = ('cd %s && ' % wd) + cmd
    print cmd
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
        cmd = ' '.join(['git clone', url, target, '&& cd %s && ' % target, 'git checkout', sha])
        return system(cmd)
    else:
        return None

def execute(git_url=None, sha=None):
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

    # run cppcheck
    results = {'success': True, 'attachments': []}
    ret = system('cppcheck src -j2 --enable=style --quiet --xml &> cppcheck.xml', wcpath)
    results['cppcheck_returncode'] = ret

    # parse xml into formatted html page
    tree = ElementTree()
    print '%s/cppcheck.xml' % wcpath
    tree.parse('%s/cppcheck.xml' % wcpath)

    with open('%s/cppcheck.html' % wcpath, 'w') as f:
        f.write('<html>\n<head>\n<title>cppcheck Results, r%s</title>\n' % sha)
        f.write('</head>\n<body>\n<h1>cppcheck Results, r%s</h1>\n' % sha)
        f.write('<style>body {margin:5px;}</style>\n')
        f.write('<table>\n<tr>\n<th>Filename</th>\n<th>Line</th>\n<th>Message</th>\n<th>Type</th>\n<th>Severity</th>\n</tr>')
        for err in tree.findall('error'):
            e = err.attrib
            f.write('<tr')
            if e['severity'] == 'error' or e['id'] in cppcheck_critical:
                results['success'] = False
                f.write(' style="color:red;font-weight:bold;"')
            if e['id'] in cppcheck_warn:
                f.write(' style="color:#F87217;font-weight:bold;"')
            f.write('>\n')
            f.write('<td>%(file)s</td>\n' % e)
            f.write('<td>%(line)s</td>\n' % e)
            f.write('<td>%(msg)s</td>\n' % e)
            f.write('<td>%(id)s</td>\n' % e)
            f.write('<td>%(severity)s</td>\n' % e)
            f.write('</tr>\n')
        f.write('\n</table>\n</body>\n</html>\n')

    # attach html to results
    attachment = {}
    with open('%s/cppcheck.html' % wcpath, 'r') as f:
        attachment = {'filename': 'cppcheck.html', 'contents': f.read(), 'link_name': 'cppcheck'}

    results['attachments'].append(attachment)

    # delete the working directory
    shutil.rmtree(os.path.abspath(wd))

    return results

if __name__ == '__channelexec__':
    kwargs = channel.receive()
    results = execute(**kwargs)
    channel.send(results)

if __name__ == '__main__':
    print execute(git_url=sys.argv[1], sha=sys.argv[2])

