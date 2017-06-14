import os
import sys

sys.stdout = sys.stderr

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))

sys.path.append('/home/grader/udacity_projects/catalog/')

from project import app as application
