#!/usr/bin/env python

#
# A simple unix/linux daemon in Python
# by Sander Marechal
#
# http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
# Accessed 18 July 2011
#
# License: CC BY-SA 3.0 -- http://creativecommons.org/licenses/by-sa/3.0/
#

import sys, time
from daemon import Daemon

class MyDaemon(Daemon):
	def run(self):
		while True:
			time.sleep(1)

if __name__ == "__main__":
	daemon = MyDaemon('/tmp/daemon-example.pid')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
