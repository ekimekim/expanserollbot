

import logging
logging.basicConfig(level='DEBUG')

import argh

from expanserollbot.main import main

argh.dispatch_command(main)
