
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from qutip import *
import qutip.control.pulseoptim as pulseoptim

def toLatex(text):
    mapping = {
        'a': r'$a$', 'a_dagger': r'$a^{\dagger}$',
        'sigma-': r'$\sigma_-$', 'sigma+': r'$\sigma_+$',
        'sigmax': r'$\sigma_x$', 'sigmay': r'$\sigma_y$',
    }
    return mapping[text] if text in mapping else text