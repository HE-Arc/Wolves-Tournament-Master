import numpy as np
from scipy import sparse
from scipy.sparse import linalg

sparse_type = sparse.csr_matrix

def sparse_states_fidelity(controls, H_drift, H_controls, inits, finals, dt=1):
    n_ctrls, plen = controls.shape
    dim = H_drift.shape[0]
    n_states = inits.shape[0]
    H_drift = dt * H_drift
    H_controls = [dt * H_c for H_c in H_controls]

    prop_forward = [None] * plen
    d_prop_forward = [[None] * n_ctrls for _ in range(plen)]
    Hs = [H_drift + sum(c*Hc for c,Hc in zip(cs, H_controls)) for cs in controls.T]
    for i, H in enumerate(Hs):
        last_state = inits.T if i == 0 else prop_forward[i-1]
        prop_forward[i] = sparse_expm_mult(H, last_state)
        print(i)
        for k, H_c in enumerate(H_controls):
            auxH = sparse.bmat([[H, H_c], [0*H, H]], format='csr')
            aux_state = sparse.bmat([[0*last_state], [last_state]], format='csr')
            d_prop_forward[i][k] = sparse_expm_mult(auxH, aux_state)[:dim]

    prop_backward = [None] * plen
    for i, H in reversed(list(enumerate(Hs))):
        last_state = finals.T if i == (plen-1) else prop_backward[i+1]
        prop_backward[i] = sparse_expm_mult(-H, last_state)
        pb1 = np.squeeze(prop_backward[i].conj().toarray())
        # pb1 = np.squeeze((linalg.expm(1j*H) * last_state).toarray())
        pb2 = np.squeeze((last_state.conj().T * linalg.expm(-1j*H)).toarray())
        # print pb1.shape, pb2.shape
        assert np.allclose(pb1, pb2), (pb1, pb2)

    ovlp = (final.conj().multiply(prop_forward[-1])).sum()
    for sf, sb in zip(prop_forward, prop_backward):
        v1 = sb.conj().multiply(sf).sum()
        assert np.allclose(v1, ovlp), (v1, ovlp)
    fid = abs(ovlp)

    d_ovlps = []
    for d_forwards, backward in zip(d_prop_forward[1:], prop_backward[:-1]):
        for d_forward in d_forwards:
            d_ovlps.append((backward.conj().multiply(d_forward)).sum())

    d_ovlps = np.array(d_ovlps).reshape((plen, n_ctrls)).T
    d_fids = (ovlp.real*d_ovlps.real + ovlp.imag*d_ovlps.imag) / (fid)
    return fid / n_states, d_fids / n_states

def sparse_expm_mult(L, rho, eps=1e-6):
    # Estimate the norm of the i*L*dt matrix
    norm_mat = linalg.norm(L,1)

    # Determine the number of time steps
    nsteps = int(np.ceil(norm_mat/5))

    # Estimate the norm of the vector
    norm_rho = linalg.norm(rho, 1)

    # Scale the vector
    rho=rho/norm_rho

    # Run the Krylov procedure (aka Taylor...)
    for n in range(nsteps):
        next_term = rho
        k = 0
        rho = 0
        while abs(next_term).max() > eps:
            rho = rho+next_term
            k = k+1
            next_term=-1j*(L*next_term)/(k*nsteps)

    # Scale the vector back
    rho = rho*norm_rho
    return rho


def sparse_d_step(H, dH, state):
    d = H.shape[0]
    zero_mat = sparse_type(H.shape)
    dUs = []
    aug_H = sparse.bmat([[H, dH], [zero_mat, H]], format='csr')
    aug_state = sparse.bmat([[0*state], [state]])
    return sparse_expm_mult(aug_H, aug_state)[:d]

if __name__ == '__main__':
    N = 5
    H = np.zeros((N, N), dtype=complex)
    dH = np.zeros((N, N), dtype=complex)
    for Hmat in (H, dH):
        for _ in range(3):
            i = np.random.randint(0, N)
            j = np.random.randint(0, N)
            v = np.random.randn() + 1j*np.random.randn()
            if i == j:
                Hmat[i, i] = v.real
            else:
                Hmat[i, j] = v
                Hmat[j, i] = v.conjugate()
    H = sparse_type(H)
    dH = sparse_type(dH)
    init = sparse_type(np.random.randn(N), dtype=complex)
    final = sparse_type(np.random.randn(N), dtype=complex)
    # print linalg.expm_multiply(-1j*H, init.T).toarray()
    # print sparse_expm_mult(H, init.T).toarray()

    s1 = sparse_expm_mult(H, init.T)
    d_s1 = sparse_d_step(H, dH, init.T)
    s2 = sparse_expm_mult(H + 1e-7*dH, init.T)
    # print ((s2 - s1) / 1e-7).toarray()
    # print d_s1.toarray()
    print(np.allclose(H.toarray(), H.conj().T.toarray()))
    print(np.allclose(dH.toarray(), dH.conj().T.toarray()))

    # U1, (dU1,) = sparse_step_propagator(H, [dH])
    controls = np.array([np.random.randn(20)])
    d_controls = np.zeros_like(controls)
    d_controls[0, 5] = 1e-7
    # import time
    # t0 = time.time()
    c1, d_c1 = sparse_states_fidelity(controls, H, [dH], init, final)
    c2, d_c2 = sparse_states_fidelity(controls + d_controls, H, [dH], init, final)
    # print (time.time() - t0) / 2.
    # H = H.toarray()
    # dH = dH.toarray()
    # init = init.toarray()
    # final = final.toarray()
    #
    # # from grape import states_fidelity
    # # t0 = time.time()
    # # c1, d_c1 = states_fidelity(controls, H, [dH], init, final)
    # # c2, d_c2 = states_fidelity(controls + d_controls, H, [dH], init, final)
    # # print (time.time() - t0) / 2.
    print((c2 - c1) / 1e-7)
    print(d_c1[0, 5])

    # U2, _ = step_propagator(H + 1e-7*dH, [dH])
    # print ((U2-U1) / 1e-7).todense()
    # print '-'*10
    # print dU1.todense()
