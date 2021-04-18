import numpy as np
import scipy.sparse
from . import pycugrape
# import sys
# sys.path.append('c:\\code\\grape\\pygrape\\cugrape')
# import pycugrape
from six.moves import reload_module
pycugrape = reload_module(pycugrape)

double = 1
rtype = np.float64 if double else np.float32
ctype = np.complex128 if double else np.complex64
NVAR, NCTRLS, PLEN, NSTATE, MAXNNZ, TAYLOR_ORDER = pycugrape.get_grape_params()

init_gpu_memory = pycugrape.init_gpu_memory


def load_states(nvar, psi0, psif):
    # assert psi0.shape == (NSTATE, DIM), (psi0.shape, (NSTATE, DIM))
    # assert psif.shape == (NSTATE, DIM), (psif.shape, (NSTATE, DIM))
    psi0_ri = np.array([psi0.real, psi0.imag]).transpose(1, 2, 0)
    psif_ri = np.array([psif.real, psif.imag]).transpose(1, 2, 0)
    pycugrape.load_states(nvar, psi0_ri, psif_ri)


def load_controls(ctrls):
    assert ctrls.shape == (PLEN, NCTRLS)
    pycugrape.load_controls(ctrls.flatten())


def get_states(nvar, dim):
    states = pycugrape.get_states(nvar, dim)
    states = states.reshape((2, NSTATE, PLEN+1, dim, 2))
    states = states[...,0] + 1j*states[...,1]
    states = states.transpose(0, 2, 3, 1)
    prop_inits = states[0]
    prop_finals = states[1][::-1]
    return prop_inits, prop_finals


def grape_step(ctrls):
    ovlp_r, ovlp_i, d_ovlp_r, d_ovlp_i = pycugrape.grape_step(ctrls)
    ovlp = ovlp_r + 1j*ovlp_i
    d_ovlp = d_ovlp_r + 1j*d_ovlp_i
    return ovlp, d_ovlp.reshape((NVAR, PLEN, NCTRLS))

# free_gpu_memory = pycugrape.free_gpu_memory
