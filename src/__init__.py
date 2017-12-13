""" Project initialization and common objects. """

import logging
import os
from pathlib import Path
import re
import sys
import pickle
from sklearn.externals import joblib

logging.basicConfig(
    stream=sys.stdout,
    format='[%(levelname)s][%(module)s] %(message)s',
    level=os.getenv('LOGLEVEL', 'info').upper()
)

workdir = Path(os.getenv('WORKDIR', '.'))

cachedir = workdir / 'cache'
cachedir.mkdir(parents=True, exist_ok=True)

#: Sets the collision systems for the entire project,
#: where each system is a string of the form
#: ``'<projectile 1><projectile 2><beam energy in GeV>'``,
#: such as ``'PbPb2760'``, ``'AuAu200'``, ``'pPb5020'``.
#: Even if the project uses only a single system,
#: this should still be a list of one system string.
systems = ['PbPb5020']


#: Design attributes 
#: keys is a list of strings describing the inputs
#: labels is a list of LaTeX labels
#: ranges is list of tuples of (min,max) for each design input
keys = ['lambda_jet','alpha_s'] #labels in words
labels = [r'\Lambda_{jet}',r'\alpha_s}'] #labels in LaTeX
ranges = [(0,1),(0,1)] 


#Design array to use
#Should be a numpy array
#If you want to generate a Latin Hypercube with a specific range, set this to None
design_array = pickle.load((cachedir / 'lhs/design_s.p').open('rb'))


#Dictionary of the model output
#Form MUST be data_list_loaded[system][observable][subobservable][{'Y','x'}]
###Note - 'Y' is an (n x p) numpy array of the output
###       'x' is a (1 x p) numpy array of numeric index of columns of Y (if exists). p_T in example below
data_list_loaded = joblib.load(filename = 'cache/model/main/full_data_dict.p')


#: Observables to emulate as a list of 2-tuples
#: ``(obs, [list of subobs])``.
observables = [('R_AA_2',[None])]

def parse_system(system):
    """
    Parse a system string into a pair of projectiles and a beam energy.

    """
    match = re.fullmatch('([A-Z]?[a-z])([A-Z]?[a-z])([0-9]+)', system)
    return match.group(1, 2), int(match.group(3))


class lazydict(dict):
    """
    A dict that populates itself on demand by calling a unary function.

    """
    def __init__(self, function, *args, **kwargs):
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __missing__(self, key):
        self[key] = value = self.function(key, *self.args, **self.kwargs)
        return value
