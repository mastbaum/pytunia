# pytunia Configuration

# Project name
project_name = 'pytunia'

## Database configuration
# URL of couchdb server
couchdb_host = 'http://localhost:5984'
# couchdb database name
couchdb_dbname = 'pytunia'

## Load balancer
from dirt.core import load_balance
load_balancer = load_balance.load

## Node configuration defaults
# When adding a new node, enable it by default?
node_enable_default = True
# Default password for newly added nodes. Currently not used.
node_password_default = 'pw123'

## Logging configuration
# Log file name
log_file = 'pytunia.log'
# List of email addresses to notify on test failure
notify_list = ['mastbaum@hep.upenn.edu']
# SMTP server required for sending email notifications
smtp_server = 'localhost'

