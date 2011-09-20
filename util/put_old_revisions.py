#!/usr/bin/env python

import time
import uuid
import couchdb

description_file = 'rat_svn_log_parsed'
meta = {}
with open(description_file, 'r') as f:
    for line in f.readlines():
        l = line.split('////')
        rev = int(l[0])
        author = l[1]
        description = l[2]
        meta[rev] = {'author': author, 'description': description}

svn_url = "https://www.snolab.ca/snoplus/svn/sasquatch/dev/rat"
tasknames = ['geoprint', 'light_yield', 'optics_response']

jsonfile = open('all_revs.json','w')
jsonfile.write('[\n')

tasknames.append('acrylic_attenuation')
tasknames.append('multipoint_uniform')
tasknames.append('multipoint_table')
tasknames.append('noise_global')
tasknames.append('fitcentroid')

for rev in range(1,624):
    if rev not in meta:
        continue

#    if rev == 104:
#        tasknames.append('acrylic_attenuation')
#    if rev == 112:
#        tasknames.append('multipoint_uniform')
#        tasknames.append('multipoint_table')
#    if rev == 189:
#        tasknames.append('noise_global')
#    if rev == 511:
#        tasknames.append('fitcentroid')
    rev_name = 'r' + str(rev)
    description  = meta[rev]['description']
    if not description: description = ''
    author = meta[rev]['author']
    record = {"_id": rev_name, "type": "record",  "description": description, "created": time.time(), 'author': author}

    cppcheck = {"_id": uuid.uuid4().get_hex(), "type": "task", "name": "cppcheck", "created": time.time(), "platform": "linux", "kwargs": {"revnumber": rev, "svn_url" : svn_url}, "record_id": rev_name}
    #print record
    #print cppcheck
    jsonfile.write(str(record) + ',')
    jsonfile.write(str(cppcheck) + ',')

    for taskname in ['acrylic_attenuation', 'fitcentroid', 'geoprint', 'light_yield', 'multipoint_table', 'multipoint_uniform', 'noise_global', 'optics_response']:
        taskid = uuid.uuid4().get_hex()
        task = {"_id": taskid, "type": "task", "name": "rattest", "created": time.time(), "platform": "linux", "kwargs": {"revnumber": rev, "svn_url" : svn_url, "testname": taskname}, "record_id": rev_name}
        #print task
        jsonfile.write(str(task) + ',')

jsonfile.write('\n]')
jsonfile.close()

