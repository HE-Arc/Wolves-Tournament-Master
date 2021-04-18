from __future__ import print_function
import numpy as np
from scipy.linalg import eigh, expm, norm
from scipy.sparse import csr_matrix, spmatrix
from math import factorial
import warnings
from functools import reduce

try:
    import qutip
except ImportError:
    qutip = None


class Setup(object):
    sparse = False
    def __init__(self, H0, Hcs, c_ops=None, loss_vec=None, sparse=False):
        self.sparse = sparse
        if c_ops is None:
            c_ops = []
        self.c_ops = c_ops = self.map_from_qobj(c_ops)
        self.H0 = self.from_qobj(H0)
        for op in c_ops:
            self.H0 += -0.5j*op.conj().T.dot(op)
        dim = self.H0.shape[0]
        assert self.H0.shape == (dim, dim)
        self.Hcs = self.map_from_qobj(Hcs)
        n_ctrls = self.Hcs.shape[0]
        if not self.sparse:
            assert self.Hcs.shape == (n_ctrls, dim, dim), self.Hcs.shape
        self.hermitian = True
        for H in [self.H0] + list(self.Hcs):
            if self.sparse:
                H = H.toarray()
            if not np.allclose(H, H.conj().T):
                print('Non-Hermitian hamiltonian detected!')
                self.hermitian = False
                break
        self.loss_vec = loss_vec

    def from_qobj(self, A, sparse=None):
        if sparse is None:
            sparse = self.sparse
        if qutip is not None and isinstance(A, qutip.Qobj):
            arr = np.squeeze(A.full())
        elif sparse and isinstance(A, spmatrix):
            return A.tocsr()
        else:
            arr = np.asarray(A).copy().astype(complex)
        if sparse and arr.ndim == 2 and arr.shape[0] == arr.shape[1]:
            return csr_matrix(arr)
        return arr

    def map_from_qobj(self, A, sparse=None):
        return np.array([self.from_qobj(a, sparse=sparse) for a in A])

    def get_fids(self, controls, aux_params, dt):
        raise NotImplementedError

    def set_dtype(self, dtype):
        self.H0 = self.H0.astype(dtype)
        self.Hcs = [Hc.astype(dtype) for Hc in self.Hcs]


class StateTransferSetup(Setup):
    r"""Optimize a problem of the form

    .. math::

        \max_\epsilon \big|\sum_k \langle \text{final}_k| U(\epsilon) |\text{init}_k\rangle\big|

    Since the absolute value is taken after the sum, this results in a coherent evolution of
    the initial states into the final states.
    """
    def __init__(self, H0, Hcs, inits, finals, c_ops=None, gauge_ops=None, loss_vec=None, coherent=True, sparse=False, use_taylor=False):
        self.use_taylor = use_taylor
        self.taylor_order = 5
        if not use_taylor:
            if sparse:
                warnings.warn('Exact (non-taylor) method incompatible with sparse matrices, using dense matrices')
            sparse = False
        super(StateTransferSetup, self).__init__(H0, Hcs, c_ops=c_ops, loss_vec=loss_vec, sparse=sparse)
        self.inits = self.map_from_qobj(inits)
        self.finals = self.map_from_qobj(finals)
        self.gauge_ops = None
        self.coherent = coherent
        if gauge_ops is not None:
            self.gauge_ops = self.map_from_qobj(gauge_ops, sparse=False)

    def optimize_taylor_order(self, max_norm, plen, dt, aux_params=None, tol=1e-6):
        if aux_params is None:
            aux_params = []
        orders = []
        for _ in range(3):
            ctrls = max_norm * np.random.randn(len(self.Hcs), plen)
            self.taylor_order = 5
            prev_psi = self.get_fids(ctrls, aux_params, dt)[0]
            rel_err = 1
            while rel_err > tol:
                self.taylor_order += 1
                psi = self.get_fids(ctrls, aux_params, dt)[0]
                rel_err = np.sum(np.abs(psi - prev_psi)**2) / np.sum(np.abs(psi)**2)
                print('Taylor order:', self.taylor_order, 'Rel Err:', rel_err)
                prev_psi = psi
            orders.append(self.taylor_order)
        self.taylor_order = max(orders)
        print('Using taylor order', self.taylor_order)

    def __getitem__(self, item):
        return [self.H0, self.Hcs, self.inits, self.finals, self.gauge_ops][item]

    def get_fids(self, controls, aux_params, dt):
        if self.use_taylor:
            return taylor_states_fidelity(
                controls, self.H0, self.Hcs,
                self.inits, self.finals, dt=dt,
                gauge_vals=aux_params, gauge_ops=self.gauge_ops, hermitian=self.hermitian,
                coherent=self.coherent, loss_vec=self.loss_vec, order=self.taylor_order
            )
        else:
            return states_fidelity(
                controls, self.H0, self.Hcs, self.inits, self.finals, dt=dt,
                gauge_vals=aux_params, gauge_ops=self.gauge_ops, hermitian=self.hermitian,
                coherent=self.coherent, loss_vec=self.loss_vec
            )

    def set_dtype(self, dtype):
        super(StateTransferSetup, self).set_dtype(dtype)
        self.inits = self.inits.astype(dtype)
        self.finals = self.finals.astype(dtype)
        if self.gauge_ops is not None:
            self.gauge_ops = self.gauge_ops.astype(dtype)

class UnitarySetup(Setup):
    r"""Optimize a problem of the form

    .. math::

        \max_\epsilon \big|\text{Tr}[U_\text{target} U(\epsilon)^\dagger]\big|
    """
    def __init__(self, H0, Hcs, U_target, c_ops=None, gauge_ops=None):
        super(UnitarySetup, self).__init__(H0, Hcs, c_ops=c_ops)
        self.U_target = self.from_qobj(U_target)
        self.gauge_ops = None
        if gauge_ops is not None:
            self.gauge_ops = self.map_from_qobj(gauge_ops)

    def __getitem__(self, item):
        return [self.H0, self.Hcs, self.U_target][item]

    def get_fids(self, controls, aux_params, dt):
        return prop_fidelity(
            controls, self.H0, self.Hcs, self.U_target, aux_params, self.gauge_ops, dt,
            hermitian=self.hermitian, loss_vec=self.loss_vec
        )

    def set_dtype(self, dtype):
        super(UnitarySetup, self).set_dtype(dtype)
        self.U_target = self.U_target.astype(dtype)
        if self.gauge_ops is not None:
            self.gauge_ops = self.gauge_ops

class ExpectationSetup(Setup):
    def __init__(self, H0, Hcs, inits, expect_ops, c_ops=None):
        super(ExpectationSetup, self).__init__(H0, Hcs, c_ops=c_ops)
        self.inits = self.from_qobj(inits) #map_from_qobj(inits)
        self.expect_ops = self.from_qobj(expect_ops) #map_from_qobj(expect_ops)

    def __getitem__(self, item):
        return [self.H0, self.Hcs, self.inits, self.expect_ops][item]

    def get_fids(self, controls, aux_params, dt):
        prop, fid, d_fid = get_expectation(controls, self.H0, self.Hcs, self.inits, self.expect_ops, dt)
        return prop, fid, d_fid, np.zeros_like(aux_params)

    def set_dtype(self, dtype):
        super(ExpectationSetup, self).set_dtype(dtype)
        self.inits = self.inits.astype(dtype)
        self.expect_ops = self.expect_ops.astype(dtype)


class LindbladSetup(StateTransferSetup):
    def __init__(self, H0, Hcs, inits, finals, c_ops, loss_vec=None, **kwargs):
        L0 = self.make_liouvillian(H0) + sum(map(self.make_dissipator, c_ops))
        Lcs = np.array(list(map(self.make_liouvillian, Hcs)))
        inits = self.map_from_qobj(inits)
        finals = self.map_from_qobj(finals)

        if inits[0].shape[0] != L0.shape[0]:
            rho_inits = [np.outer(i1, i2.conj()).flatten() for i1 in inits for i2 in inits]
            rho_finals = [np.outer(f1, f2.conj()).flatten() for f1 in finals for f2 in finals]
        else:
            rho_inits = inits
            rho_finals = finals

        super(LindbladSetup, self).__init__(L0, Lcs, rho_inits, rho_finals, **kwargs)
        # self.hermitian = False

    def get_fids(self, controls, aux_params, dt):
        prop, fid, d_fid, d_fid_aux = super(LindbladSetup, self).get_fids(controls, aux_params, dt)
        fid = np.sqrt(fid)
        d_fid = d_fid / fid
        d_fid_aux = d_fid_aux / fid
        return prop, fid, d_fid, d_fid_aux


    def make_liouvillian(self, H):
        H = self.from_qobj(H)
        I = np.eye(H.shape[0])
        return (np.kron(I, H) - np.kron(H.T, I))


    def make_dissipator(self, c_op):
        c_op = self.from_qobj(c_op)
        cd = c_op.T.conj()
        c = c_op
        cdc = cd.dot(c)
        I = np.eye(c_op.shape[0])
        return 1j * (np.kron(cd.T, c) - 0.5 * (np.kron(I, cdc) + np.kron(cdc.T, I)))


class SubspaceSetup(StateTransferSetup):
    def get_fids(self, controls, aux_params, dt):
        assert not self.use_taylor
        return states_fidelity(
            controls, self.H0, self.Hcs, self.inits, self.finals, dt=dt,
            gauge_vals=aux_params, gauge_ops=self.gauge_ops, hermitian=self.hermitian,
            coherent=False, subspace_contain=True, loss_vec=self.loss_vec
        )


def states_fidelity(controls, H_drift, H_controls, inits, finals, gauge_vals=None, gauge_ops=None,
                    dt=1, hermitian=True, coherent=True, subspace_contain=False, loss_vec=None):
    n_ctrls, plen = controls.shape
    n_states = len(inits)
    use_gauge = gauge_ops is not None
    dim = H_drift.shape[0]
    H_drift = dt * H_drift
    H_controls = dt * np.array(H_controls)

    # TODO: Don't re-initialize every time if possible
    props = np.empty((plen, dim, dim), H_drift.dtype)
    d_props = np.empty((n_ctrls, plen, dim, dim), H_drift.dtype)
    for i, time_slice in enumerate(controls.T):
        H = H_drift + sum(c*Hc for c,Hc in zip(time_slice, H_controls))
        if hermitian:
            props[i], d_props[:, i, :, :] = step_propagator(H, H_controls, loss_vec)
        else:
            props[i], d_props[:, i, :, :] = step_propagator_nonhermitian(H, H_controls)

    if use_gauge:
        g_sum = sum(g_val*g_op for g_val, g_op in zip(gauge_vals, gauge_ops))
        g_prop, d_g_props = step_propagator(g_sum, gauge_ops)
        props = np.concatenate((props, [g_prop]))

    prop_inits = [inits.T]
    for prop in props:
        prop_inits.append(prop.dot(prop_inits[-1]))
    prop_finals = [finals.conj()]
    for prop in reversed(props):
        prop_finals.append(prop_finals[-1].dot(prop))
    prop_finals.reverse()

    if coherent:
        ovlp = np.sum(prop_finals[-1].T * prop_inits[-1])
        fid = abs(ovlp)
        d_ovlps = []
        for i, (pi, pf) in enumerate(zip(prop_inits[:plen], prop_finals[1:])):
            for d_prop in d_props[:, i]:
                d_ovlps.append(np.sum(pf.T * d_prop.dot(pi)))
        d_ovlps = np.array(d_ovlps).reshape((plen, n_ctrls)).T
        d_fids = (ovlp.real*d_ovlps.real + ovlp.imag*d_ovlps.imag) / (fid)
    elif subspace_contain:
        ovlps = prop_finals[-1].dot(prop_inits[-1])
        a_ovlps = np.abs(ovlps)**2
        fid = np.sum(a_ovlps)
        d_fids = []
        for i, (pi, pf) in enumerate(zip(prop_inits[:plen], prop_finals[1:])):
            for d_prop in d_props[:, i]:
                d_ovlp = pf.dot(d_prop.dot(pi))
                d_a_ovlps = 2 * (ovlps.real*d_ovlp.real + ovlps.imag*d_ovlp.imag)
                d_fids.append(np.sum(d_a_ovlps))
        d_fids = np.array(d_fids).reshape((plen, n_ctrls)).T
    else:
        ovlps = np.sum(prop_finals[-1].T * prop_inits[-1], axis=0)
        a_ovlps = np.abs(ovlps)**2
        fid = np.sum(a_ovlps)
        d_fids = []
        for i, (pi, pf) in enumerate(zip(prop_inits[:plen], prop_finals[1:])):
            for d_prop in d_props[:, i]:
                d_ovlp = pf.T * d_prop.dot(pi)
                d_a_ovlps = 2 * (ovlps.real*d_ovlp.real + ovlps.imag*d_ovlp.imag)
                d_fids.append(np.sum(d_a_ovlps))
        d_fids = np.array(d_fids).reshape((plen, n_ctrls)).T


    if not use_gauge:
        return prop_inits[-1], fid / n_states, d_fids / n_states, []

    d_g_ovlps = []
    pi = prop_inits[-2]
    pf = prop_finals[-1]
    for d_prop in d_g_props:
        d_g_ovlps.append(np.sum(pf.T * d_prop.dot(pi)))
    d_g_ovlps = np.array(d_g_ovlps)
    d_g_fids = (ovlp.real*d_g_ovlps.real + ovlp.imag*d_g_ovlps.imag) / (fid)

    return prop_inits[-1], fid / n_states, d_fids / n_states, d_g_fids / n_states


def get_expectation(controls, H_drift, H_controls, init, expect_op, dt=1):
    H_drift = dt * H_drift
    H_controls = dt * np.array(H_controls)
    tot_prop, d_tot_props, _ = total_propagator(controls, H_drift, H_controls)
    final = tot_prop.dot(init)
    d_finals = np.einsum('ijkl,l->ijk', d_tot_props, init)
    expect = final.conj().T.dot(expect_op).dot(final).real
    d_op_finals = np.einsum('ij,klj->kli', expect_op, d_finals)
    d_expects = 2*np.einsum('i,jki->jk', final.conj(), d_op_finals).real
    return tot_prop, expect, d_expects


def prop_fidelity(controls, H_drift, H_controls, U_target, gauge_vals, gauge_ops, dt=1,
                  hermitian=True, loss_vec=None):
    """
    Get the total propagator as well as the fidelity to a given target
    defined as abs(Tr(U_target . U.conj().T)) and the gradient of the fidelity
    with respect to the controls
    """
    H_drift = dt * H_drift
    H_controls = dt * np.array(H_controls)
    tot_prop, d_tot_props, d_g_props = total_propagator(
        controls, H_drift, H_controls, gauge_vals, gauge_ops, hermitian=hermitian, loss_vec=loss_vec
    )
    return prop_fidelity_from_U(tot_prop, d_tot_props, d_g_props, U_target)


def prop_fidelity_from_U(U, dUs, d_g_Us, U_target):
    norm = np.sum(abs(U_target)**2)
    overlap = np.sum(U_target.conj() * U) / norm
    d_overlaps = np.sum(U_target.conj() * dUs, axis=(2,3)) / norm
    fid = abs(overlap)
    d_fid = (overlap.real*d_overlaps.real + overlap.imag*d_overlaps.imag) / fid
    if len(d_g_Us) == 0:
        d_g_fid = []
    else:
        d_g_overlaps = np.sum(U_target.conj() * d_g_Us, axis=(1,2)) / norm
        d_g_fid = (overlap.real*d_g_overlaps.real + overlap.imag*d_g_overlaps.imag) / fid
    return U, fid, d_fid, d_g_fid


def total_propagator(controls, H_drift, H_controls, gauge_vals=None, gauge_ops=None,
                     hermitian=True, loss_vec=None):
    """
    Compute step propagator for each time point and take product
    to find the total propagator. Similarly find the derivative
    of the propagator with respect to the controls.

    :param controls: (N_CTRLS, PLEN) real array
    :param H_drift: (DIM, DIM) complex array
    :param H_controls: (N_CTRLS, DIM, DIM) complex array
    :return: (U_total, [d(U_total)/d(controls)])
    """
    n_ctrls, plen = controls.shape
    dim = H_drift.shape[0]
    use_gauge = gauge_ops is not None

    props = np.empty((plen, dim, dim), H_drift.dtype)
    d_props = np.empty((n_ctrls, plen, dim, dim), H_drift.dtype)
    for i, time_slice in enumerate(controls.T):
        H = H_drift + sum(c*Hc for c,Hc in zip(time_slice, H_controls))
        if hermitian:
            props[i], d_props[:, i, :, :] = step_propagator(H, H_controls, loss_vec)
        else:
            props[i], d_props[:, i, :, :] = step_propagator_nonhermitian(H, H_controls)

    if use_gauge:
        g_sum = sum(g_val*g_op for g_val, g_op in zip(gauge_vals, gauge_ops))
        g_prop, d_g_props = step_propagator(g_sum, gauge_ops)
        props = np.concatenate((props, [g_prop]))

    ahead = [np.identity(dim)]
    for prop in props[:-1]:
        ahead.append(prop.dot(ahead[-1]))

    behind = [np.identity(dim)]
    for prop in reversed(props[1:]):
        behind.append(behind[-1].dot(prop))
    behind.reverse()

    tot_prop = props[-1].dot(ahead[-1])
    d_tot_props = [list(map(mdot, list(zip(behind, d_props[i], ahead)))) for i in range(n_ctrls)]
    if not use_gauge:
        return tot_prop, np.array(d_tot_props), []
    d_g_tot_props = [mdot((behind[-1], d_prop, ahead[-1])) for d_prop in d_g_props]
    return tot_prop, np.array(d_tot_props), np.array(d_g_tot_props)


def total_propagator_only(controls, H_drift, H_controls, gauge_vals=None, gauge_ops=None,
                     hermitian=True, loss_vec=None, step_props=False):

    n_ctrls, plen = controls.shape
    dim = H_drift.shape[0]
    use_gauge = gauge_ops is not None

    props = np.empty((plen, dim, dim), H_drift.dtype)
    for i, time_slice in enumerate(controls.T):
        H = H_drift + sum(c*Hc for c,Hc in zip(time_slice, H_controls))
        if hermitian:
            props[i] = step_propagator(H, H_controls, loss_vec, prop_only=True)
        else:
            props[i] = step_propagator_nonhermitian(H, H_controls, prop_only=True)

    if use_gauge:
        raise NotImplemented # not tested
        g_sum = sum(g_val*g_op for g_val, g_op in zip(gauge_vals, gauge_ops))
        g_prop, d_g_props = step_propagator(g_sum, gauge_ops)
        props = np.concatenate((props, [g_prop]))

    ahead = [np.identity(dim)]
    for prop in props[:-1]:
        ahead.append(prop.dot(ahead[-1]))

    tot_prop = props[-1].dot(ahead[-1])

    if step_props:
        return tot_prop, props
    return tot_prop



def step_propagator_nonhermitian(A, Bs, n=3, beta=0.1, prop_only=False):
    d = max(int(np.ceil(np.log2(norm(A)/beta))), 0)
    X = -1j*A / 2**d
    Ys = [-1j*B / 2**d for B in Bs]
    X2 = X / 2
    eX2 = expm(X2)
    eX = eX2.dot(eX2)
    
    if prop_only:
        eA = eX
        for k in range(d):
            eA = eA.dot(eA)
        return eA
        
    coef = lambda k: 1.0 / factorial(2*k + 1)
    deXs = []
    for Y in Ys:
        G = coef(n)*Y
        for k in reversed(list(range(n))):
            C1 = G.dot(X2) - X2.dot(G)
            C2 = C1.dot(X2) - X2.dot(C1)
            G = coef(k)*Y + C2
        deXs.append(eX2.dot(G).dot(eX2))

    eA = eX
    deAs = deXs
    for k in range(d):
        deAs = [eA.dot(deA) + deA.dot(eA) for deA in deAs]
        eA = eA.dot(eA)
    return eA, deAs


def step_propagator(H, dHs, loss_vec=None, prop_only=False):
    """
    Compute e^(-i*H) and (matrix-valued) derivatives in
    the directions Hc for Hc in Hcs.

    See doi:10.1006/aama.1995.1017, equation (7)

    :param H: hermitian matrix to take exponential of
    :param dHs: list of hermitian matrices to take derivatives in the direction of
    :return: (prop, grads)
    """
    vals, basis = eigh(H)
    i_vals = -1j*vals
    basis_hc = basis.conj().T
    prop = (np.exp(i_vals) * basis).dot(basis_hc)
    if prop_only:
        return prop

    # Loewner matrix G
    z = -(i_vals.reshape((-1, 1)) - i_vals)
    z_mask = abs(z) < 1e-8
    G = np.zeros_like(z)
    G[~z_mask] = (np.exp(z[~z_mask]) - 1) / z[~z_mask]
    G[z_mask] = 1 + z[z_mask] / 2

    left = prop.dot(basis) # todo: eliminate this operation by adjusting G
    d_props = []
    for dH in dHs:
        inner = G * basis_hc.dot(dH.dot(basis))
        d_prop = -1j * left.dot(inner.dot(basis_hc))
        d_props.append(d_prop)

    if loss_vec is not None:
        prop = (loss_vec * prop.T).T
        d_props = [(loss_vec * d_prop.T).T for d_prop in d_props]

    return prop, np.array(d_props)


def get_unitary(controls, H_drift, H_controls, dt):
    U = np.eye(H_drift.shape[0])
    for i, time_slice in enumerate(controls.T):
        H = H_drift + sum(c*Hc for c,Hc in zip(time_slice, H_controls))
        U = expm(-1j*H*dt).dot(U)
    return U


def mdot(ops):
    """
    Take the dot product of an arbitrary number of terms
    """
    return reduce(np.dot, ops)


def taylor_states_fidelity(controls, H0, Hcs, inits, finals, dt=1, gauge_vals=None, gauge_ops=None,
                           hermitian=True, coherent=True, loss_vec=None, order=5):
    if gauge_ops is not None and len(gauge_ops) == 0:
        gauge_ops = None
    if gauge_ops is not None:
        assert len(gauge_ops) == len(gauge_vals)
    nctrls, plen = controls.shape
    n_states, dim = inits.shape
    if isinstance(H0, np.ndarray):
        H0_hc = H0.conj().T
        Hcs_hc = [hc.conj().T for hc in Hcs]
    else:
        H0_hc = H0.conj().T.tocsr()
        Hcs_hc = [hc.conj().T.tocsr() for hc in Hcs]

    if gauge_ops is not None:
        g_sum = sum(g_val*g_op for g_val, g_op in zip(gauge_vals, gauge_ops))
        g_prop, d_g_props = step_propagator(g_sum, gauge_ops)

    # Propagate forward, with derivative
    prop_inits = [inits.T]
    d_prop_inits = []
    for cs in controls.T:
        L = -1j*dt*(H0 + sum(c*Hc for c, Hc in zip(cs, Hcs)))
        psi = prop_inits[-1].copy()
        # Next psi is sum over taylor terms psi_k = (L^k)/(k!)psi_0
        psi_k = psi
        d_psis = [0]*len(Hcs)
        d_psi_ks = [np.zeros_like(psi) for _ in range(len(Hcs))]
        for k in range(1, order+1):
            for i, Hc in enumerate(Hcs):
                d_psi_ks[i] = (L.dot(d_psi_ks[i]) + -1j*dt*Hc.dot(psi_k)) / k
                d_psis[i] += d_psi_ks[i]
            psi_k = L.dot(psi_k) / k
            psi += psi_k
        if loss_vec is not None:
            psi = (loss_vec * psi.T).T
            d_psis = [(loss_vec * d_psi.T).T for d_psi in d_psis]
        prop_inits.append(psi)
        d_prop_inits.append(d_psis)
    if gauge_ops is not None:
        d_prop_inits.append([dg.dot(prop_inits[-1]) for dg in d_g_props])
        prop_inits.append(g_prop.dot(prop_inits[-1]))

    # Propagate backward, derivative not needed
    prop_finals = [finals.T]
    if gauge_ops is not None:
        prop_finals.append(g_prop.conj().T.dot(prop_finals[-1]))

    for cs in reversed(controls.T):
        Lhc = 1j*dt*(H0_hc + sum(c*Hc for c, Hc in zip(cs, Hcs_hc)))
        psi = prop_finals[-1].copy()
        if loss_vec is not None:
            psi = (loss_vec * psi.T).T
        psi_k = psi
        for k in range(1, order+1):
            psi_k = Lhc.dot(psi_k) / k
            psi += psi_k
        prop_finals.append(psi)
    prop_finals.reverse()

    # Compute fid
    if coherent:
        ovlp = np.sum(prop_finals[-1].conj() * prop_inits[-1]) / n_states
        fid = abs(ovlp)
    else:
        ovlps = np.sum(prop_finals[-1].conj() * prop_inits[-1], axis=0)
        a_ovlps = np.abs(ovlps)**2
        fid = np.sum(a_ovlps) / n_states

    # Check overlaps
    # for pi, pf in zip(prop_inits, prop_finals):
    #     ovlp2 = np.sum(pf.conj() * pi) / n_states
    #     assert np.allclose(ovlp, ovlp2), (ovlp, ovlp2)

    # Compute d_fid / d_controls
    d_fids = []
    if coherent:
        for i, prop_final in enumerate(prop_finals[1:]):
            for d_prop_init in d_prop_inits[i]:
                d_ovlp = np.sum(prop_final.conj() * d_prop_init) / n_states
                d_fids.append((d_ovlp.real * ovlp.real + d_ovlp.imag * ovlp.imag) / fid)
    else:
        for i, prop_final in enumerate(prop_finals[1:]):
            for d_prop_init in d_prop_inits[i]:
                d_ovlp = prop_final.conj() * d_prop_init
                d_a_ovlps = 2 * (ovlps.real*d_ovlp.real + ovlps.imag*d_ovlp.imag)
                d_fids.append(np.sum(d_a_ovlps) / n_states)

    d_g_fids = np.array([])
    if gauge_ops is not None:
        ng = len(gauge_ops)
        d_g_fids = np.array(d_fids[-ng:])
        d_fids = d_fids[:-ng]
    d_fids = np.array(d_fids).reshape((plen, nctrls)).T

    return prop_inits[-1], fid, d_fids, d_g_fids

if __name__ == '__main__':
    from .preparations import random_hermitian
    dim = 5
    n_gauge = 3
    n_ctrls = 2
    plen = 10
    idx = 0
    _, U_target = eigh(random_hermitian(dim))
    H0 = random_hermitian(dim)
    Hcs = [random_hermitian(dim) for _ in range(n_ctrls)]
    gauge_ops = [random_hermitian(dim) for _ in range(n_gauge)]
    gauge_vals = np.random.randn(n_gauge)
    controls = np.random.randn(n_ctrls, plen)
    d_gauge_vals = np.zeros(n_gauge)
    _, c1, g1, g2 = prop_fidelity(controls, H0, Hcs, U_target, gauge_vals, gauge_ops)
    # print g1
    # print g2
    gauge_vals[idx] += 1e-7
    # controls[0, 5] += 1e-7
    _, c2, _, _ = prop_fidelity(controls, H0, Hcs, U_target, gauge_vals, gauge_ops)
    g3 = 1e7 * (c2 - c1)
    # print g1[0, 5]
    print(g2[idx])
    print(g3)
