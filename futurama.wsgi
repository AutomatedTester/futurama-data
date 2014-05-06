activate_this = '/var/www/future/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
sys.path.insert(0, '/var/www/futurama-data/')

from app import app as application