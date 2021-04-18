import numpy as np
from scipy.linalg import eigh, eigvalsh, pinv, norm, eig, expm
from .preparations import random_hermitian
np.set_printoptions(precision=3, linewidth=150)

def floquet_operator(controls, H0, Hcs, n_freq, t_max):
    I_sys = np.eye(H0.shape[0])
    NF = 2*n_freq + 1
    I_freq = np.eye(NF)
    nus = np.arange(-n_freq, n_freq+1)
    N_freq = np.diag(nus)
    omega = 2 * np.pi / t_max
    K = np.kron(I_sys, omega * N_freq).astype(complex)
    K += np.kron(H0, I_freq)
    K0 = K.copy()
    Kcs = np.zeros((len(nus), len(Hcs)) + K.shape, complex)
    for i, (nu, control_row) in enumerate(zip(nus, controls.T)):
        pi_nu = np.diag(np.ones(2*n_freq + 1 - abs(nu)), nu)
        for j, (Hc, control) in enumerate(zip(Hcs, control_row)):
            Kcs[i, j] = np.kron(control*Hc, pi_nu)
            K += Kcs[i, j]
    return K, K0, Kcs

def prop_grad(K, K0, Kcs, n_freq, t_max):
    NF = 2*n_freq + 1
    dim = K.shape[0] / NF
    idxs = (n_freq*dim, (n_freq+1)*dim-1)
    e_vals, e_vecs = eigh(K, eigvals=idxs)
    e_vecs = e_vecs.reshape((dim, NF, dim))
    inits = e_vecs.sum(axis=1)

    # Ik_invs = K0[None,...] - e_vals[:, None, None]
    # Iks = []
    # for Ik_inv in Ik_invs:
    #     Iks.append(pinv(Ik_inv))

    # d_e_vals = np.einsum('ij,kljm,mi->kli', e_vecs.conj().T, Kcs, e_vecs)
    # Kcb, _ = np.broadcast_arrays(Kcs, Ids, d_e_vals)
    # Tkijs = Kcb - d_e_vals
    # d_e_vecs = np.einsum
    # inits = np.array([i / norm(i) for i in inits.T]).T

    finals = np.exp(-1j*e_vals*t_max) * inits
    prop = finals.dot(inits.conj().T)
    return prop

if __name__ == '__main__':

    # from numpy import pi
    # from qutip import sigmax, sigmaz, floquet_modes, propagator
    # delta = 0.2 * 2*pi; eps0 = 1.0 * 2*pi; A = 1 * 2.5 * 2*pi; omega = 1.0 * 2*pi
    # H0 = - delta/2.0 * sigmax() - eps0/2.0 * sigmaz()
    # H1 = A/2.0 * sigmaz()
    # args = {'w': omega}
    # H = [H0, [H1, 'cos(w * t)']]
    # T = 2*pi / omega
    # U = propagator(H, T, [], args)
    # f_modes, f_energies = floquet_modes(H, T, args, U=U)
    # print f_energies
    # print f_modes

    dim = 2
    t_max = .2
    nf = 10
    # H0 = H0.full()
    # Hc = H1.full()
    H0 = random_hermitian(dim)
    Hc = random_hermitian(dim)
    ws = np.arange(-nf, nf+1) * 2 * np.pi / t_max
    f_controls = np.random.randn(1, 2*nf+1)
    f_controls = f_controls + f_controls[:, ::-1]
    # f_controls = np.zeros((1, 2*nf+1))
    # f_controls[0, nf+1] = f_controls[0, nf-1] = .5
    # print f_controls
    ts = np.linspace(0, t_max, 100)
    t_controls = np.array([
        sum([c*np.exp(1j*w*ts) for w, c in zip(ws, fcs)])
        for fcs in f_controls
    ]).real
    K, K0, Kcs = floquet_operator(f_controls, H0, [Hc], nf, t_max)
    evs = eigvalsh(K).reshape((2*nf+1, dim))
    # print 2 * np.pi / t_max
    # print evs
    # print evs[1:,:] - evs[:-1,:]
    # print (evs + np.pi / t_max) % (2 * np.pi / t_max) - np.pi / t_max
    # print np.allclose(K, K.conj().T)
    # print K.shape
    # print K0.shape
    # print Kcs.shape
    prop1 = prop_grad(K, K0, Kcs, nf, t_max)
    from . import grape
    dt = ts[1]
    prop2, _ = grape.total_propagator(t_controls, H0*dt, [Hc*dt])
    # print prop1.dot(prop1.conj().T)
    # print prop2.dot(prop2.conj().T)
    print(prop1)
    print(prop2)
    # print U.full()
    # vals, vecs = eig(U.full())
    # import matplotlib.pyplot as plt
    # plt.plot(ts, t_controls[0])
    # plt.plot(ts, np.cos(omega * ts))
    # plt.show()



