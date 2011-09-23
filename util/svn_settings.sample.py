# settings for post-commit hook
#
#  svn_co_url - URL for svn checkout by pytunia nodes
#  changeset_base_url - URL to view changesets. rev number is appended 
#  test_path - relative path of functional tests
#  db_host - Hostname:port of CouchDB server 
#  db_name - Name of CouchDB database
#  db_user - Username of CouchDB user 
#  db_password - Password for CouchDB user 

svn_co_url = 'http://www.yoursite.com/project/svn/public'
changeset_base_url = 'http://www.yoursite.com/project/Trac/changeset/'
test_path = 'test/functional'
db_host = 'pytunia.server.com:5984'
db_name = 'pytunia'
db_user = 'couchdb user'
db_pass = 'couchdb pass'

