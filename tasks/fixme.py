import os
import sys
import shutil
import uuid
import subprocess
from xml.etree.ElementTree import ElementTree

def system(cmd, wd=None):
    '''a wrapper for subprocess.call, which executes cmd in working directory
    wd in a bash shell, returning the exit code.'''
    if wd:
        cmd = ('cd %s && ' % wd) + cmd
    print cmd
    return subprocess.call([cmd], executable='/bin/bash', shell=True)

def svn_co(url, rev, target, username=None, password=None, wd=None):
    '''check out a revision from an svn server, optionally providing a
    username and password. the arguments are parsed as::

        cd [wd] && svn co [url] -r [rev] [target] --username=[username] \
    --password=[password]
    '''
    if wd:
        target = os.path.join(wd, target)
    target = os.path.abspath(target)
    if not os.path.exists(target):
        cmd = ' '.join(['svn co', url, '-r', rev, target])
        if username: cmd = ' '.join([cmd, '--username=%s' % username])
        if password: cmd = ' '.join([cmd, '--password=%s' % password])
        return system(cmd)
    else:
        return None

def svn_blame(fname, rev, username=None, password=None, wd=None):
    '''get annotated source from an svn server, optionally providing a
    username and password. the arguments are parsed as::

        cd [wd] && svn blame --xml [file]@[rev]
    '''
    cmd = 'svn blame --xml %s@%s' % (fname, rev)
    if username: cmd = ' '.join([cmd, '--username=%s' % username])
    if password: cmd = ' '.join([cmd, '--password=%s' % password])
    cmd = cmd + ' &> blame.xml'
    return system(cmd, wd), os.path.join(wd, 'blame.xml')

def execute(svn_url=None, svn_user=None, svn_pass=None, revnumber=None):
    if not revnumber:
        return {'success': False, 'reason': 'missing revision number'}
    if not svn_url:
        return {'success': False, 'reason': 'missing svn url'}

    revnumber = str(revnumber)

    # temporary working directory
    wd = str(uuid.uuid4())
    os.mkdir(wd)

    # get the code
    ret = svn_co(svn_url, revnumber, revnumber, username=svn_user, password=svn_pass, wd=wd)
    if ret is None or ret != 0:
        return {'success': False, 'reason': 'svn co failed'}
    wcpath = os.path.join(wd, revnumber)

    # find instances of fixme
    results = {'success': True, 'attachments': []}
    ret = system('grep -irn --color --exclude=*.svn-base fixme . &> fixme.txt', wcpath)
    results['grep_returncode'] = ret

    # parse grep output into formatted html page
    with open(os.path.join(wcpath,'fixme.html'),'w') as fo:
        fo.write('<html>\n<head>\n<title>FIXME Detector</title>\n</head>\n')
        fo.write('<body>\n<h1>Instances of "fixme" in source tree</h1>\n')
        fo.write('<table border>\n<tr>\n<th>File</th>\n<th>Line</th>\n')
        fo.write('<th>Code</th>\n<th>Last Edited</th>\n</tr>')
        with open(os.path.join(wcpath,'fixme.txt'),'r') as fi:
            for item in fi.readlines():
                fname = item.split(':', 2)[0]
                line = item.split(':', 2)[1]
                code = item.split(':', 2)[2].lstrip()
                fo.write('<tr>\n<td>%s</td>\n<td>%s</td>\n<td>%s</td>\n' % (fname, line, code))

                last_revision = ''
                last_author = ''
                ret, blamefile = svn_blame(fname, revnumber, wd=wcpath)
                if ret == 0:
                    with open(blamefile, 'r') as fb:
                        tree = ElementTree()
                        tree.parse(fb)
                        for elem in tree.findall('target/entry'):
                            if elem.attrib['line-number'] == str(line):
                                last_revision = elem.find('commit').attrib['revision']
                                last_author = elem.find('commit/author').text
                fo.write('<td>%s, r%s</td>\n</tr>\n' % (last_author, last_revision))

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
    print execute(svn_url=sys.argv[1], revnumber=sys.argv[2])

