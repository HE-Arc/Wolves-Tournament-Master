import sys
from pygrape.cugrape.configure_cugrape import AnnihilateMode, CreateMode, configure
import qutip as q

mode_dim_variations = [[2, 10, 10], [2, 11, 10]]

def destroy(n):
    ops = [q.qeye(d) for d in mode_dims]
    ops[n] = q.destroy(mode_dims[n])
    return q.tensor(*list(reversed(ops)))

def get_Hs(numeric=False):
    if numeric:
        a, b, c = map(destroy, range(3))
        ad, bd, cd = a.dag(), b.dag(), c.dag()
    else:
        a, b, c = map(AnnihilateMode, range(3))
        ad, bd, cd = map(CreateMode, range(3))
    kerr_1 = kerr_2 = 1e-5
    chi_1 = chi_2 = 1e-3
    drive = 1e-2
    H0 = (kerr_1/2)*(bd*bd*b*b)
    H0 += (kerr_2/2)*(cd*cd*c*c)
    H0 += chi_1*ad*a*bd*b
    H0 += chi_2*ad*a*cd*c
    Hxq = drive*(a + ad)
    Hyq = 1j*drive*(a - ad)
    Hx1 = drive*(b + bd)
    Hy1 = 1j*drive*(b - bd)
    Hx2 = drive*(c + cd)
    Hy2 = 1j*drive*(c - cd)
    Hs = [H0, Hxq, Hyq, Hx1, Hy1, Hx2, Hy2]
    if numeric:
        Hs = [H.data.tocsr() for H in Hs]
    return Hs


if int(sys.argv[1]):
    configure(mode_dims, get_Hs(), 300, 1, 20, True)

import time
from pygrape.cugrape import cugrape
from pygrape.cugrape.cugrape import NVAR, NCTRLS, NSTATE, PLEN, MAXNNZ, TAYLOR_ORDER
import scipy.sparse
import scipy.linalg
import numpy as np
import cpusetup
np.set_printoptions(linewidth=250)



# Hs = [-0.5j*scipy.sparse.rand(DIM, DIM, float(MAXNNZ)/(2*DIM*DIM), 'csr') for _ in range(NCTRLS+1)]
# for H in Hs:
    # H.data *= np.exp(-1j*np.random.randn(len(H.data)))
# Hs = [(H + H.conj().T).tocsr() for H in Hs]
# assert all(H.getnnz() <= MAXNNZ for H in Hs)


for i, ds in enumerate(mode_dims):
    np.random.seed(12345)
    psi0 = np.random.randn(NSTATE, DIM) + 1j*np.random.randn(NSTATE, DIM)
    psi0 /= np.linalg.norm(psi0, axis=1)
    psif = np.random.randn(NSTATE, DIM) + 1j*np.random.randn(NSTATE, DIM)
    psif /= np.linalg.norm(psif, axis=1)
# def randH():
#     H = np.random.randn(DIM, DIM) + 1j*np.random.randn(DIM, DIM)
#     return H + H.conj().T
# def randU():
#     return scipy.linalg.expm(-1j*randH())
# def randStates():
#     return randU()[:NSTATE]

# psi0 = randStates()
# psif = randStates()
# ctrls = np.random.randn(PLEN, NCTRLS)
ctrls = np.ones((PLEN, NCTRLS))
d_ctrls = np.random.randn(PLEN, NCTRLS)


Hs_n = get_Hs(numeric=True)
ret = cpusetup.run(Hs_n, ctrls, psi0, psif, TAYLOR_ORDER)
cpu_prop_inits, cpu_prop_finals, cpu_ovlp, cpu_d_ovlps = ret
cpu_ovlp2 = cpusetup.run(Hs_n, ctrls+1e-7*d_ctrls, psi0, psif, TAYLOR_ORDER)[-2]
print('Estimated Gradient', 1e7*(cpu_ovlp2 - cpu_ovlp))
print('Calculated Gradient', np.sum(d_ctrls * cpu_d_ovlps))


cugrape.init_gpu_memory()
# cugrape.load_hamiltonians(Hs)
cugrape.load_states(psi0, psif)
cugrape.load_controls(ctrls)
cugrape.prop_states()
# cugrape.norm_states()
gpu_prop_inits, gpu_prop_finals = cugrape.get_states()
# cugrape.difference_states()
# gpu_prop_diffs, _ = cugrape.get_states()
cugrape.compute_overlaps()
gpu_ovlp, gpu_d_ovlps = cugrape.get_ovlp()
# gpu_cost, gpu_d_cost = cugrape.get_cost()
# cugrape.free_gpu_memory()
# gpu_cost *= PLEN
# gpu_d_cost *= PLEN


def checkarr(name, a, b):
    a = np.array(a)
    b = np.array(b)
    print(name, np.abs(a - b).max(), np.linalg.norm(a), np.linalg.norm(b))

print('CPU init norm', np.linalg.norm(cpu_prop_inits[0]))
print('GPU init norm', np.linalg.norm(gpu_prop_inits[0]))
print('CPU Final norm', np.linalg.norm(cpu_prop_inits[-1]))
print('GPU Final norm', np.linalg.norm(gpu_prop_inits[-1]))
# print(np.array(cpu_prop_inits).real.mean(axis=(1,2)))
# print(np.array(gpu_prop_inits).real.mean(axis=(1,2)))
checkarr('Prop Inits', cpu_prop_inits, gpu_prop_inits)
checkarr('Prop Finals', cpu_prop_finals, gpu_prop_finals)
checkarr('Overlap', cpu_ovlp, gpu_ovlp)
checkarr('Grad Overlaps', cpu_d_ovlps, gpu_d_ovlps)
# checkarr('Prop Diffs', cpu_prop_diffs, gpu_prop_diffs)
# checkarr('Grad Cost', cpu_d_cost, gpu_d_cost)
# checkarr('Cost', cpu_cost, gpu_cost)
# print(cpu_prop_inits[0][:5,0])
# print(gpu_prop_inits[0][:5,0])
# print(cpu_prop_inits[1][:5,0])
# print(gpu_prop_inits[1][:5,0])
# print(cpu_prop_inits[1][:5,0] - gpu_prop_inits[1][:5,0])
# print(cpu_prop_inits[2][:5,0] - cpu_prop_inits[1][:5,0])
# print(gpu_prop_inits[2][:5,0] - gpu_prop_inits[1][:5,0])
# print(abs(np.array(cpu_prop_inits) - np.array(gpu_prop_inits)).max(axis=(1,2)))
