from math import pi, sqrt
import numpy as np
import qutip
from scipy import interpolate, optimize


def make_ops(nc, nq):
    a = qutip.tensor(qutip.qeye(nq), qutip.destroy(nc))
    ad = a.dag()
    b = qutip.tensor(qutip.destroy(nq), qutip.qeye(nc))
    bd = b.dag()
    return a, ad, b, bd


def make_hmt(nc, nq, chi, chi_prime, kerr, anharm, q_drive, c_drive, qobj=False, delta_q=0, delta_c=0, drive_prime=0):
    a, ad, b, bd = make_ops(nc, nq)
    n_op = ad * a

    H0 = 2 * pi * b.dag() * b * (chi*n_op + chi_prime/2.*ad*ad*a*a)
    H0 += 2 * pi * b.dag() * b * delta_q
    H0 += 2 * pi * a.dag() * a * delta_c
    H0 += (2 * pi * kerr / 2) * ad * ad * a * a
    H0 += (2 * pi * anharm / 2) * bd * bd * b * b

    d_b = b * (1 + drive_prime * n_op)
    d_bd = d_b.dag()
    HD_I = 2 * pi * q_drive * (d_b + d_bd)
    HD_Q = 2j * pi * q_drive * (d_b - d_bd)

    HDC_I = 2 * pi * c_drive * (a + ad)
    HDC_Q = 2j * pi * c_drive * (a - ad)
    if qobj:
        return H0, (HD_I, HD_Q, HDC_I, HDC_Q)

    H0 = H0.full()
    HD_I = HD_I.full()
    HD_Q = HD_Q.full()
    HDC_I = HDC_I.full()
    HDC_Q = HDC_Q.full()
    H0, Hcs = H0, np.array([HD_I, HD_Q, HDC_I, HDC_Q])

    return H0, Hcs


def make_c_ops(nc, nq, t1, t2, t1_cav, t2_cav=None):
    a, ad, b, bd = make_ops(nc, nq)
    c_ops = [
        np.sqrt(1. / t1) * b,
        np.sqrt(1. / t2) * bd * b,
        np.sqrt(1. / t1_cav) * a,
    ]
    if t2_cav is not None:
        c_ops.append(np.sqrt(1. / t2_cav) * ad * a)
    return c_ops


def make_target(nf, nq, ptype, n_bit, n_bits):
    id_list = lambda: [qutip.qeye(2) for _ in range(n_bits+1)]
    x_ops = [id_list() for _ in range(n_bits)]
    z_ops = [id_list() for _ in range(n_bits)]
    h_ops = [id_list() for _ in range(n_bits)]
    ih_ops = [id_list() for _ in range(n_bits)]
    cx_ops = []
    m_cz_ops = []
    m_cx_ops = []
    m_cy_ops = []

    for i in range(n_bits):
        z_ops[i][i+1] = qutip.sigmaz()
        x_ops[i][i+1] = qutip.sigmax()
        h_ops[i][i+1] = qutip.hadamard_transform()
        ih_ops[i][i+1] = qutip.Qobj([[-1, 1], [-1j, -1j]]) / sqrt(2)
        z_ops[i] = qutip.tensor(*z_ops[i])
        x_ops[i] = qutip.tensor(*x_ops[i])
        h_ops[i] = qutip.tensor(*h_ops[i])
        ih_ops[i] = qutip.tensor(*ih_ops[i])
        cx_ops.append(qutip.controlled_gate(qutip.hadamard_transform(), n_bits+1, i+1, 0))
        m_cz_ops.append(qutip.controlled_gate(qutip.sigmax(), n_bits+1, i+1, 0))
        m_cx_ops.append(h_ops[i] * m_cz_ops[i] * h_ops[i])
        m_cy_ops.append(ih_ops[i] * m_cz_ops[i] * ih_ops[i])

    for ops in (x_ops, z_ops, h_ops, m_cz_ops, m_cx_ops, m_cy_ops):
        ops.reverse()

    bits_n = 2**n_bits
    flip_target = id_list()
    flip_target[0] = qutip.sigmax()
    flip_target = qutip.tensor(*flip_target)
    if ptype == 'i':
        targ = qutip.tensor(*id_list())
    elif ptype == 'mz':
        targ = m_cz_ops[n_bit-1] * flip_target
    elif ptype == 'mx':
        targ = m_cx_ops[n_bit-1]
    elif ptype == 'my':
        targ = m_cy_ops[n_bit-1]
    elif ptype == 'x':
        targ = x_ops[n_bit-1]
    elif ptype == 'z':
        targ = z_ops[n_bit-1]
    U = np.zeros((nq*nf, nq*nf), dtype=np.complex)
    U[:bits_n, :bits_n] = targ[:bits_n, :bits_n]
    U[nf:nf+bits_n, :bits_n] = targ[bits_n:, :bits_n]
    U[:bits_n, nf:nf+bits_n] = targ[:bits_n, bits_n:]
    U[nf:nf+bits_n, nf:nf+bits_n] = targ[bits_n:, bits_n:]
    mask_c = np.zeros(nf)
    mask_c[:bits_n] = 1
    mask_q = np.zeros(nq)
    mask_q[:2] = 1
    mask = np.kron(mask_q, mask_c)
    mask = np.arange(len(mask))[mask == 1]
    return U, mask


def random_pulse(plen, npoints=50):
    ysr = np.concatenate([[0,], 2*np.random.random(npoints) - 1, [0,]])
    ysg = interpolate.interp1d(np.arange(npoints+2), ysr, kind='cubic')
    return ysg(np.linspace(0, npoints+1, plen))

def random_waves(n_ctrls, plen, npoints=50):
    return np.array([random_pulse(plen, npoints) for _ in range(n_ctrls)])

def get_drive_strength(dim, anharm, amp, sig):
    ts = np.linspace(-2*sig, 2*sig, 4*sig)
    pulse = amp*np.exp(-ts**2 / (2*sig**2))
    b = qutip.destroy(dim)
    bd = b.dag()
    H0 = 2 * pi * (anharm / 2) * bd * bd * b * b
    Hd = 2 * pi * (b + bd)
    ts = np.arange(len(pulse))
    psi0 = qutip.basis(dim)

    def cost(amp):
        H = [H0, [amp[0]*Hd, pulse]]
        ret = qutip.mesolve(H, psi0, ts, [], [bd * b])
        cost = (1 - ret.expect[0][-1])**2
        print(amp, cost)
        return cost

    return optimize.fmin(cost, 1e-3 / max(abs(pulse)))[0]

def unitary_to_states(U):
    inits = []
    finals = []
    sz = U.shape[0]
    for i in range(sz):
        if np.count_nonzero(U[i,:]) > 0:
            inits.append(np.zeros(sz, dtype=np.complex128))
            inits[-1][i] = 1
            finals.append(U[i,:])
    return np.array(inits), np.array(finals)

def random_hermitian(dim):
    H = np.random.randn(dim, dim) + 1j*np.random.randn(dim, dim)
    return H + H.conj().T
