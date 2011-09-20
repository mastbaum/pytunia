#!/usr/bin/env python

import sys

def main(fname):
    ofile = open(fname+'_parsed', 'w')
    with open(fname,'r') as f:
        line = f.readline()
        while line:
            if line[:10] == ('-' * 10):
                line = f.readline()
                if line == '':
                    break
                meta = [i.strip(' ') for i in line.split('|')]
                rev = int(meta[0][1:])
                author = meta[1]
                print rev, author,
                ofile.write('%s////%s////' % (rev, author))

                # burn a few
                line = f.readline()
                line = f.readline()
                description = []
                while line[:10] != ('-' * 10):
                    description.append(line)
                    line = f.readline()

                description = '<br>'.join(description).replace('\n','<br>').replace("\'","").replace("\"","").rstrip('<br>')
                print description
                ofile.write('%s\n' % description)

    ofile.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:', sys.argv[0], '[filename]'
        sys.exit(1)
    else:
        main(sys.argv[1])

