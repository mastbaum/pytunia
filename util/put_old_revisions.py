#!/usr/bin/env python

import sys
import os
import subprocess
import time
import uuid
import json

def parse_svn_log(svn_url):
    '''extract revision number, author, and description from svn log output,
    and turn it into a dictionary.
    '''
    revisions = {}
    svn_log = subprocess.Popen(['svn', 'log', svn_url], stdout=subprocess.PIPE).communicate()[0]
    with open('svn_log_temp','w') as f:
        f.write(svn_log)
    with open('svn_log_temp','r') as f:
        line = f.readline()
        while line:
            # better done with regex...
            if line[:10] == ('-' * 10):
                line = f.readline()
                if line == '':
                    break
                meta = [i.strip(' ') for i in line.split('|')]
                rev = int(meta[0][1:])
                author = meta[1]
                revisions[rev] = {'author': author}

                # burn a few lines
                line = f.readline()
                line = f.readline()
                description = []
                while line[:10] != ('-' * 10):
                    description.append(line)
                    line = f.readline()

                description = '\n'.join(description).rstrip('\n')
                revisions[rev]['description'] = description

    os.remove('svn_log_temp')
    return revisions

def main(svn_url, start=1, stop=None):
    '''loop over the requested revisions to generate json to load into the
    pytunia database.
    '''
    revisions = parse_svn_log(svn_url)
    if stop is None:
        stop = max(revisions)

    start = int(start)
    stop = int(stop)

    docs = []
    for rev in range(start, stop):
        # revisions can be missing
        if rev not in revisions:
            continue

        # get task names with svn list
        tasknames = []
        for item in subprocess.Popen(['svn', 'list', svn_url + '/test/full', '-r', str(rev)], stdout=subprocess.PIPE).communicate()[0].split():
            tasknames.append(item.rstrip('/'))

        # record (revision) document
        rev_name = 'r' + str(rev)
        description  = revisions[rev]['description']
        if not description:
            description = ' '
        author = revisions[rev]['author']
        record = {"_id": rev_name, "type": "record",  "description": description, "created": time.time(), 'author': author}
        docs.append(record)

        # cppcheck task document
        cppcheck = {"_id": uuid.uuid4().get_hex(), "type": "task", "name": "cppcheck", "created": time.time(), "platform": "linux", "kwargs": {"revnumber": rev, "svn_url" : svn_url}, "record_id": rev_name}
        docs.append(cppcheck)

        # rattest task documents
        for taskname in tasknames:
            taskid = uuid.uuid4().get_hex()
            task = {"_id": taskid, "type": "task", "name": "rattest", "created": time.time(), "platform": "linux", "kwargs": {"revnumber": rev, "svn_url" : svn_url, "testname": taskname}, "record_id": rev_name}
            docs.append(task)

    docs_json = json.dumps(docs)

    print docs_json

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage:', sys.argv[0], '<svn url> [start_rev=1] [end_rev=HEAD]'
        sys.exit(1)
    else:
        main(*sys.argv[1:])

