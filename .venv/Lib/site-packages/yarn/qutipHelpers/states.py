
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from qutip import *
import qutip.control.pulseoptim as pulseoptim

def cat(cavityDimension,alpha,N=2):
    psis = [coherent(cavityDimension, np.exp(2j*np.pi*n/N)*alpha) 
            for n in range(N)]
    return sum(psis).unit()