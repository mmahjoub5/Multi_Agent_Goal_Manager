import sys
from os.path import dirname, abspath

# Add the project root to the Python path
print(abspath(dirname(dirname(__file__))))
sys.path.insert(0, abspath(dirname(dirname(__file__))))