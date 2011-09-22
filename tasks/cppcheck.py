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

def execute(svn_url=None, diff=None, svn_user=None, svn_pass=None, revnumber=None):
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
    wcpath = os.path.abspath(os.path.join(wd, revnumber))

    # patch if a diff is provided
    # diffs are uuencoded to be json-friendly
    if diff is not None:
        diff_filename = os.path.join(wcpath, wd + '.diff')
        with open(diff_filename, 'w') as diff_file:
            diff_file.write(diff.decode('uu'))
        cmd = 'patch --binary -p0 -i %s' % diff_filename
        ret = system(cmd, wcpath)
        if ret != 0:
            return {'success': False, 'reason': 'failed to apply patch'}

    # run cppcheck
    results = {'success': True, 'attachments': []}
    ret = system('cppcheck src -j2 --enable=style --quiet --xml &> cppcheck.xml', wcpath)
    results['cppcheck_returncode'] = ret

    # parse xml into formatted html page
    tree = ElementTree()
    print '%s/cppcheck.xml' % wcpath
    tree.parse('%s/cppcheck.xml' % wcpath)

    with open('%s/cppcheck.html' % wcpath, 'w') as f:
        f.write('<html>\n<head>\n<title>cppcheck Results, r%s</title>\n' % revnumber)
        f.write('</head>\n<body>\n<h1>cppcheck Results, r%s</h1>\n' % revnumber)
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
    print execute(svn_url=sys.argv[1], revnumber=sys.argv[2])

