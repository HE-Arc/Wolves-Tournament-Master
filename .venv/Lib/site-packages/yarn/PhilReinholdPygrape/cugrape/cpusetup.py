import time
import scipy.sparse
import scipy.linalg
import numpy as np

double = 1
rtype = np.float64 if double else np.float32
ctype = np.complex128 if double else np.complex64

def run(Hs, ctrls, psi0, psif, taylor_order):
    Hs = [-1j*H for H in Hs]
    Hs_ct = [H.conj().T.tocsr() for H in Hs]
    plen, nctrls = ctrls.shape

    def prop_psi(cs, psi, ct=False, grad=False, printinfo=False):
        _Hs = Hs_ct if ct else Hs
        H = _Hs[0] + sum(c*Hc for c, Hc in zip(cs, _Hs[1:]))
        H = H.astype(ctype)
        psi_k = psi
        psi_out = psi_k.copy()
        d_psi_k = [np.zeros_like(psi) for _ in range(nctrls)]
        d_psi_out = [np.zeros_like(psi) for _ in range(nctrls)]
        dHs = []
        if grad:
            dHs = _Hs[1:]
        for k in range(1, taylor_order+1):
            for n, dH in enumerate(dHs):
                d_psi_k[n] = (dH.dot(psi_k) + H.dot(d_psi_k[n])) / k
                d_psi_out[n] += d_psi_k[n]
            psi_k = H.dot(psi_k) / k
            psi_out += psi_k
            # if printinfo:
                # print('A', k, psi_out[0,0].real, psi_k[0,0].real)
        if grad:
            return psi_out, np.array(d_psi_out)
        return psi_out

    t0 = time.time()
    prop_inits = [psi0.T.astype(ctype)]
    for i, cs in enumerate(ctrls):
        prop_inits.append(prop_psi(cs, prop_inits[-1], printinfo=(i == 0)))

    prop_finals = [psif.T.astype(ctype)]
    for cs in reversed(ctrls):
        prop_finals.append(prop_psi(cs, prop_finals[-1], ct=1))
    t1 = time.time()
    print('CPU time', t1-t0)
    prop_finals = list(reversed(prop_finals))

    d_ovlps = []
    t = 0
    for cs, psi1, psi2 in zip(ctrls, prop_inits[:-1], prop_finals[1:]):
        p_psi1, d_p_psi1 = prop_psi(cs, psi1, grad=True)
        if t == 0:
            print('B', d_p_psi1[0,0,0], psi2[0,0])
        d_ovlps.append(np.sum(psi2.conj() * d_p_psi1, axis=(1,2)))
        t += 1


    ovlps = np.sum(np.array(prop_inits) * np.array(prop_finals).conj(), axis=(1,2))
    assert np.allclose(ovlps, ovlps[0]), ovlps

    return prop_inits, prop_finals, ovlps[0], d_ovlps


if __name__ == '__main__':
    dim = 5
    maxnnz = 20
    nctrls = 2
    nstate = 3
    plen = 8
    taylor_order = 20
    double = 1

    Hs = [-0.01j*scipy.sparse.rand(dim, dim, float(maxnnz)/(dim*dim), 'csr') for _ in range(nctrls+1)]
    for H in Hs:
        H.data *= np.exp(-1j*np.random.randn(maxnnz))
    # Hs = [H - H.conj().T for H in Hs]

    def randH():
        H = np.random.randn(dim, dim) + 1j*np.random.randn(dim, dim)
        return H + H.conj().T
    def randU():
        return scipy.linalg.expm(-1j*randH())
    def randStates():
        return randU()[:nstate]

    psi0 = randStates()
    psif = randStates()

    ctrls = np.random.randn(plen, nctrls)
    d_ctrls = np.random.randn(plen, nctrls)

    c1, dc = run(Hs, ctrls, psi0, psif, taylor_order)[-2:]
    c2, _  = run(Hs, ctrls + 1e-7*d_ctrls, psi0, psif, taylor_order)[-2:]

    a = 1e7*(c2 - c1)
    b = (dc * d_ctrls).sum()
    print(a, b, a/b)


