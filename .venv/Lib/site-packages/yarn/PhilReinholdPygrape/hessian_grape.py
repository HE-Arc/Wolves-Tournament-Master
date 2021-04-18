import numpy as np
from scipy.linalg import eigh
from scipy.optimize import minimize
from .grape import states_fidelity

def subsample_hash(a):
    rng = np.random.RandomState(89)
    inds = rng.randint(low=0, high=a.size, size=100)
    b = a.flat[inds]
    b.flags.writeable = False
    return hash(b.data)


def hessian_grape(init_controls, H_drift, H_controls, init_states, final_states):
    n_ctrls = len(H_controls)
    import time
    t0 = time.time()

    class NCGFunc(object):
        xhash = None
        fid_hess = None

        def cost_and_grad(self, controls):
            xhash = subsample_hash(controls)
            if xhash != self.xhash:
                self.xhash = xhash
                controls = controls.reshape((n_ctrls, -1))
                self.fid, grad = states_fidelity(
                    controls, H_drift, H_controls, init_states, final_states
                )
                self.fid_grad = grad.flatten()
                self.fid_hess = None
                print('fprime', np.sqrt(self.fid), 'time', time.time() - t0)
            return 1 - self.fid, -self.fid_grad

        def get_hess(self, controls):
            xhash = subsample_hash(controls)
            if xhash != self.xhash or self.fid_hess is None:
                self.xhash = xhash
                controls = controls.reshape((n_ctrls, -1))
                self.fid, self.fid_grad, self.fid_hess = states_fidelity_hessian(
                    controls, H_drift, H_controls, init_states, final_states
                )
                print('hess', np.sqrt(self.fid), 'time', time.time() - t0)
            return -self.fid_hess
    ncgfunc = NCGFunc()
    ret = minimize(ncgfunc.cost_and_grad, init_controls, jac=True, hess=ncgfunc.get_hess, method='trust-ncg')
    print(ret.message)
    return ret.x


def states_fidelity_hessian(controls, H_drift, H_controls, inits, finals, dt=1):
    n_ctrls, plen = controls.shape
    n_states = len(inits)
    dim = H_drift.shape[0]
    H_drift = dt * H_drift
    H_controls = dt * np.array(H_controls)

    props = np.empty((plen, dim, dim), np.complex128)
    d_props = np.empty((n_ctrls, plen, dim, dim), np.complex128)
    d2_props = np.empty((n_ctrls, n_ctrls, plen, dim, dim), np.complex128)
    for i, time_slice in enumerate(controls.T):
        H = H_drift + sum(c*Hc for c,Hc in zip(time_slice, H_controls))
        props[i], d_props[:, i, :, :], d2_props[:, :, i, :, :] = step_propagator(H, H_controls)

    # prop_inits[t] = U_t ... U_1|init>
    prop_inits = np.zeros((plen, dim, n_states), complex)
    # prop_d1_inits[t1,n,t2] = U_t1 ... dU_t1/dx_n ... |init>
    prop_d1_inits = np.zeros((plen, n_ctrls, plen, dim, n_states), complex)
    # prop_d2_inits[n1,t1,n2,t2] = dU_t1/dx_n1 ... dU_t2/dx_n2 ... |init>
    prop_d2_inits = np.zeros((n_ctrls, plen, n_ctrls, plen, dim, n_states), complex)

    for t1 in range(plen):
        last_state = prop_inits[t1-1] if t1 else inits.T
        prop_inits[t1] = props[t1].dot(last_state)
        prop_d1_inits[t1,:,:t1] = np.einsum('ij,kljm->klim', props[t1], prop_d1_inits[t1-1,:,:t1])
        for i1 in range(n_ctrls):
            prop_d1_inits[t1, i1, t1] = d_props[i1, t1].dot(last_state)
            for i2 in range(i1, n_ctrls):
                v = d2_props[i1,i2,t1].dot(last_state)
                prop_d2_inits[i1,t1,i2,t1] = prop_d2_inits[i2,t1,i1,t1] = v
        prop_d2_inits[:,t1,:,:t1] = np.einsum('ijk,lmkn->ilmjn', d_props[:, t1], prop_d1_inits[t1-1,:,:t1])

    # prop_finals[t] = <final| U_N ... U_(t+1)
    prop_finals = np.zeros((plen, n_states, dim), complex)
    prop_finals[plen-1] = finals.conj()
    for t in reversed(list(range(plen-1))):
        prop_finals[t] = prop_finals[t+1].dot(props[t+1])

    ovlp = np.sum(finals.conj().T * prop_inits[-1])
    d_ovlps = np.einsum('ij,klji->kl', finals.conj(), prop_d1_inits[plen-1]).flatten()
    d2_ovlps = np.einsum('ijk,limnkj->limn', prop_finals, prop_d2_inits)
    d2_ovlps = d2_ovlps.reshape((n_ctrls*plen, -1))
    d2_ovlps = d2_ovlps + d2_ovlps.T
    d2_ovlps[np.diag_indices(n_ctrls*plen)] /= 2
    d_ovlps = d_ovlps.flatten()
    d2_ovlps = d2_ovlps.reshape((n_ctrls*plen, -1))

    fid = abs(ovlp)**2
    f, g = ovlp.real, ovlp.imag
    df, dg = d_ovlps.real, d_ovlps.imag
    d2f, d2g = d2_ovlps.real, d2_ovlps.imag
    d_fids = 2*(f*df + g*dg)
    d2_fids = 2*(f*d2f + g*d2g + np.outer(df, df) + np.outer(dg, dg))
    return fid / n_states**2, d_fids / n_states**2, d2_fids / n_states**2


def step_propagator(H, dHs):
    d = H.shape[0]
    L0, V = eigh(H)
    L = -1j*L0
    Vd = V.conj().T
    D = L.reshape((-1, 1)) - L
    mask = abs(D) < 1e-7
    expL = np.exp(L)
    U = (expL * V).dot(Vd)
    DexpL = expL.reshape((-1, 1)) - expL

    # Ignore warnings from zero-division for now
    err_settings = np.seterr(all='ignore')
    Dinv = 1 / D
    G = DexpL * Dinv
    expL_D = expL[:,None] * Dinv
    DexpL_D2 = DexpL * Dinv**2
    expL_D_D = np.einsum('i,ij,ik->ijk', expL, Dinv, Dinv)
    np.seterr(**err_settings)

    _, G_ii = np.broadcast_arrays(G, expL)
    G[mask] = G_ii[mask]
    d1Us = []
    dHBs = [Vd.dot(dH).dot(V) for dH in dHs]
    for dHB in dHBs:
        d1Us.append(-1j*V.dot(G * dHB).dot(Vd))

    mask_ij = mask[:, :, None]
    mask_ik = mask[:, None, :]
    mask_jk = mask[None, :, :]
    mask_ijk = mask_ij & mask_ik & mask_jk
    G = expL_D_D + expL_D_D.transpose(1, 2, 0) + expL_D_D.transpose(2, 0, 1)
    G2 = expL_D - DexpL_D2
    # i is close to j, approximate L[j] with L[i]
    _, G2_ij, mask_ij = np.broadcast_arrays(G, G2[:, None, :], mask_ij)
    # j is close to k, approximate L[k] with L[j]
    _, G2_jk, mask_jk = np.broadcast_arrays(G, G2.T[:, :, None], mask_jk)
    # i is close to k, approximate L[k] with L[i]
    _, G2_ik, mask_ik = np.broadcast_arrays(G, G2[:, :, None], mask_ik)
    G[mask_ij] = G2_ij[mask_ij]
    G[mask_ik] = G2_ik[mask_ik]
    G[mask_jk] = G2_jk[mask_jk]
    G[mask_ijk] = ((expL / 2)[:, None, None] * np.ones((d, d, d)))[mask_ijk]

    ndh = len(dHs)
    d2Us = np.empty((ndh, ndh, d, d), complex)
    for i in range(ndh):
        K = np.einsum('ijk,ij,jk->ik', G, dHBs[i], dHBs[i])
        d2Us[i, i] = -2 * V.dot(K).dot(Vd)
        for j in range(i+1, ndh):
            K1 = np.einsum('ijk,ij,jk->ik', G, dHBs[i], dHBs[j])
            K2 = np.einsum('ijk,ij,jk->ik', G, dHBs[j], dHBs[i])
            d2Us[i, j] = d2Us[j, i] = -V.dot(K1 + K2).dot(Vd)
    return U, d1Us, d2Us

if __name__ == '__main__':
    n_ctrls = 2
    dim = 40
    plen = 400
    n_states = 1
    # np.random.seed(12345)

    def random_hermitian():
        H = np.random.randn(dim, dim) + 1j*np.random.randn(dim, dim)
        return H + H.conj().T

    H0 = random_hermitian()
    Hcs = np.array([random_hermitian() for _ in range(n_ctrls)])
    inits = eigh(random_hermitian())[1][:, :n_states].T
    finals = eigh(random_hermitian())[1][:, :n_states].T
    init_ctrls = np.random.randn(n_ctrls, plen)

    # hessian_grape(init_ctrls, H0, Hcs, inits, finals)
    # from grape import run_grape
    # from reporting import print_costs
    # run_grape(init_ctrls, [(H0, Hcs, inits, finals)], reporters=[print_costs()])

    # d_ctrls = np.zeros_like(init_ctrls)
    # i, j = 1, 5
    # ij = plen*i + j
    # d_ctrls[i, j] = 1e-7

    U1, d1U1, d2U1 = step_propagator(H0, Hcs)
    U2, d1U2, d2U2 = step_propagator(H0 + 1e-7*Hcs[0], Hcs)
    print(1e7 * (U2 - U1) / d1U1[0])
    print(1e7 * (d1U2[1] - d1U1[1]) / d2U2[0,1])

    # f1, df1 = states_fidelity(init_ctrls, H0, Hcs, inits, finals)
    # f2, df2 = states_fidelity(init_ctrls + d_ctrls, H0, Hcs, inits, finals)
    # print (f2 - f1) / 1e-7
    # print df1.reshape((n_ctrls, plen))[1, 5]
    # import timeit
    # setup = 'from __main__ import states_fidelity_hessian, init_ctrls, H0, Hcs, inits, finals'
    # print timeit.timeit('states_fidelity_hessian(init_ctrls, H0, Hcs, inits, finals)', setup, number=10) / 10

    # f1, df1, d2f = states_fidelity_hessian(init_ctrls, H0, Hcs, inits, finals)
    # f2, df2, _   = states_fidelity_hessian(init_ctrls + d_ctrls, H0, Hcs, inits, finals)
    # print f1
    # print (f2 - f1) / 1e-7
    # print df1[ij]
    # k = 3
    # print (df2[k] - df1[k]) / 1e-7
    # print d2f[k, ij]
    # print d2f[ij, k]
    # print '-'*10
    # from grape import states_fidelity
    # f1, df1 = states_fidelity(init_ctrls, H0, Hcs, inits, finals)
    # print '-'*10
    # print f1
    # print df1.flatten()[ij]


