import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from basics.setup import One_shot_parameters
from main import main

pars = One_shot_parameters() # Get the parameters
main(pars)