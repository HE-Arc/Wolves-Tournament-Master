from __future__ import print_function
import matplotlib
# matplotlib.use('agg')
import os

import numpy as np
from scipy.linalg import eigh
from .preparations import random_waves
from scipy.optimize import minimize
try:
    from scipy.optimize import OptimizeResult
except:
    class OptimizeResult(object):
        def __init__(self, **kwargs):
            [setattr(self, key, val) for key, val in list(kwargs.items())]
from .reporters import print_costs
from .setups import Setup
import multiprocessing
try:
    import qutip
except ImportError:
    qutip = None

N_ITER = 0

class OptFinishedException(Exception):
    def __init__(self, msg, controls):
        super(OptFinishedException, self).__init__(msg)
        self.controls = controls

def get_impulse_response(Nfft, dt, filt_func, thresh=1e-2, **kwargs):
    Ns = Nfft//2 + 1
    fs = np.fft.fftfreq(Nfft, dt)
    S = filt_func(fs, **kwargs)
    # Compute cepstrum
    c = np.fft.ifft(np.log(S))
    # Reflect anti-causal zeros to lie within the unit circle
    cf = np.concatenate([
        [c[0]], c[1:Ns-1]+c[Nfft:Ns-1:-1],
        [c[Ns-1]], np.zeros(Nfft-Ns)
    ])
    # Invert cepstrum to get minimum phase causal spectrum
    Smp = np.exp(np.fft.fft(cf))
    response = np.fft.ifft(Smp).real
    # Truncate response by trimming near-zero elements
    w = np.argwhere((abs(response) / max(abs(response))) > thresh).flatten()[-1]
    w = max(1, w)
    ret = response[:w]
    ret /= ret.sum()
    return ret


def create_outdir(outdir):
    if outdir is None:
        return None
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    iter_num = 0
    while os.path.exists(os.path.join(outdir, str(iter_num))):
        iter_num += 1
    outdir = os.path.join(outdir, str(iter_num))
    os.mkdir(outdir)
    return outdir


class GrapeResults(object):
    def __init__(self, data, opt_result):
        self.controls = data['sim_controls']
        self.aux_params = data['aux_params']
        self.dt = data['dt']
        self.raw_controls = data['raw_controls']
        self.awg_controls = data['awg_controls']
        self.response = data['response']
        self.props = data['props']
        self.fids = data['fids']
        self.fids_hist = data['fids_hist']
        self.fid_grads = data['fid_grads']
        self.pen_costs = data['pen_costs']
        self.pen_grads = data['pen_grads']
        self.tot_cost = data['tot_cost']
        self.tot_grad = data['tot_grad']
        self.shape_func = data['shape_func']
        self.outdir = data['outdir']
        if opt_result is not None:
            self.message = opt_result.message
            self.success = opt_result.success
            self.status = opt_result.status
            self.nfev = opt_result.nfev
            self.nit = opt_result.nit
        self.ts = self.dt * np.arange(self.controls.shape[1])


def run_setup(args):
    setup, controls, aux_params, sim_dt = args
    return setup.get_fids(controls, aux_params, sim_dt)


def run_grape(init_controls, setups, penalty_fns=None, reporter_fns=None,
              outdir=None, dt=1, n_ss=1, init_aux_params=None, filt_func=None,
              test_cost=False, shape_sigma=10, shape_array=None, n_proc=1, discrepancy_penalty=0,
              discrepancy_idcs=[],
              dtype=None, response=None, save_data=0, eval_once=False, impulse_data=None,
              ssb=0, term_fid=None, check_grad=0, freq_range=None, **opts):
    """
    Run BFGS in order to minimize the infidelity of 
    unitary implemented by the controls

    Args:
        init_controls ([N_CTRLS, PLEN] real array): 
            initial guess for the control array
        setups (List of tuples): 
            Each tuple consists of either 3 elements 
            (H drift, H controls, U target) or 4 elements 
            (H drift, H controls, init states, final states)

            - H drift ([DIM, DIM] complex array)
            - H controls ([N_CTRLS, DIM, DIM] complex array)
            - U target ([DIM, DIM] complex array)
            - init/final states: ([N_STATES, DIM] complex array)

            If any of these elements are qutip Qobjects 
            automatic conversion will be attempted
        penalty_fns (List of callables):
            Each function should take the controls as an 
            argument and should return a (cost, gradient) 
            tuple
        reporter_fns (List of callables):
            Functions used for status reporting. 
            The argument names are extracted from the 
            function itself, and used to supply the 
            necessary data to the function. 
        outdir (str):
            Output directory. Created if it does not exist. 
            Output is put in a numbered subdirectory of 
            outdir, which prevents overwriting old results.
        dt (float):
            time step size of the control waveforms
        n_ss (int):
            factor by which to sub-sample the controls
        filt_func (callable):
            a filter function that returns the response 
            versus frequency, e.g. a Gaussian lambda 
            >>> fs: exp(-fs**2/(2*sigma**2))
        test_cost (int or bool):
            if nonzero, run specified number of tests of 
            the gradient to ensure its accuracy. 
            The minimization is not performed
        shape_sigma (float):
            Specifies the width of the shape function, 
            which forces the amplitude to go to zero 
            smoothly at the beginning and end of the pulse.
        n_proc (int):
            If using multiple setups, multiple processors 
            can be used to run each setup in parallel.
            This specifies the number of processes to use. 
            There is no advantage to setting this number
            larger than the number of setups.
        discrepancy_penalty (float)
            If using multiple setups, penalize the 
            discrepancy sum(F_k - mean({F_k}) of the 
            fidelitie F_k
        dtype (numpy dtype)
            Set the dtype used to do calculations. 
            Set to np.complex64 if speed is valued over 
            precision
        opts (dict)
            additional arguments are passed to minimizer.
            see `scipy.optimize.minimize <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-bfgs.html>`_
    """
    if isinstance(setups, Setup):
        setups = [setups]
    init_controls = np.array(init_controls)
    n_ctrls, plen = init_controls.shape
    ctrl_size = n_ctrls * plen
    penalty_fns = penalty_fns or []
    fids_hist = []
    pen_hist = []
    if reporter_fns is None:
        reporter_fns = [print_costs()]
    if init_aux_params is None:
        init_aux_params = []
    outdir = create_outdir(outdir)
    if outdir is None:
        outdir = '.'

    ts = np.arange(plen, dtype=float) * dt
    sim_dt = dt / float(n_ss)
    if shape_sigma > 0:
        shape_func = 1 - np.exp(-ts / shape_sigma) - np.exp(-(ts[-1]-ts) / shape_sigma)
    else:
        shape_func = 1
    if not (shape_array is None):
        shape_func = shape_array
        
    if impulse_data is None:
        impulse_data = np.eye(n_ss)[0]
    if filt_func:
        response = get_impulse_response(plen*n_ss, sim_dt, filt_func)
        impulse_data = np.ones(n_ss)
    if response is not None and ssb != 0:
        response = response * np.exp(1j * 2 * np.pi * np.arange(len(response))*ssb*sim_dt)
    if response is not None:
        c_response = np.any(response.imag != 0)
    if response is not None and response.ndim == 1:
        if c_response:
            response = np.array([response] * (n_ctrls/2))
        else:
            response = np.array([response] * n_ctrls)

    if n_proc > 1:
        pool = multiprocessing.Pool(n_proc)

    if dtype is not None:
        for setup in setups:
            setup.set_dtype(dtype)

    aux_precon = 1
    if len(init_aux_params) > 0:
        for s in setups:
            _, _, d_ctrls, d_aux = run_setup((s, init_controls, init_aux_params, sim_dt))
            if abs(d_aux).max() > 0:
                aux_precon = max(min(aux_precon, .5 * abs(d_ctrls).max() / abs(d_aux).max()), 1e-3)
    init_aux_params = np.array(init_aux_params) / aux_precon

    def get_report_data(controls, force_report=False):
        raw_controls, aux_params = np.split(controls, [ctrl_size])
        raw_controls = raw_controls.reshape((n_ctrls, plen))
        controls = full_controls = awg_controls = raw_controls * shape_func
        aux_params = aux_precon * aux_params

        if n_ss != 1:
            controls = np.kron(controls, impulse_data)
        if response is not None:
            if c_response:
                c_controls = controls[::2] + 1j*controls[1::2]
                c_controls = np.array([
                    np.convolve(c_controls[i,:], response[i], mode='full')
                    for i in range(n_ctrls/2)
                ])
                controls = np.array([c_controls.real, c_controls.imag])
                full_controls = controls.transpose(1,0,2).reshape((n_ctrls, -1))
                controls = full_controls
            else:
                controls = np.array([
                    np.convolve(controls[i,:], response[i], mode='full')
                        for i in range(n_ctrls)])

        args = [(s, controls, aux_params, sim_dt) for s in setups]
        if n_proc > 1:
            results = pool.map(run_setup, args)
        else:
            results = list(map(run_setup, args))

        props, fids, fid_grads, aux_fid_grads = [], [], [], []
        for prop, fid, d_fid, d_fid_aux in results:
            props.append(prop)
            if isinstance(fid, (list, tuple, np.ndarray)):
                fids.extend(fid)
                aux_fid_grads.extend(d_fid_aux)
                d_fids = d_fid
            else:
                fids.append(fid)
                aux_fid_grads.append(d_fid_aux)
                d_fids = [d_fid]

            for d_fid in d_fids:
                # Average according to response function / up-sampling
                if response is not None:
                    if c_response:
                        c_d_fid = d_fid[::2] + 1j*d_fid[1::2]
                        rev_resp = response[:,::-1].conj()
                        # rev_resp = np.hstack((rev_resp, np.zeros((n_ctrls/2, 1))))
                        c_d_fid = np.array([
                            np.convolve(rev_resp[i], c_d_fid[i], mode='valid')
                            for i in range(n_ctrls/2)
                        ])
                        d_fid = np.array([c_d_fid.real, c_d_fid.imag])
                        d_fid = d_fid.transpose(1,0,2).reshape((n_ctrls, -1))
                    else:
                        d_fid = np.array([
                            np.convolve(d_fid[i,:], response[i, ::-1], mode='valid')
                                for i in range(n_ctrls)])
                if n_ss != 1:
                    d_fid = (impulse_data * d_fid.reshape((n_ctrls, plen, n_ss))).sum(axis=2)

                fid_grads.append(d_fid * shape_func)
        fids_hist.append(fids)

        pen_costs, pen_grads = [], []
        for fn in penalty_fns:
            pen_cost, pen_grad = fn(awg_controls)
            pen_costs.append(pen_cost)
            pen_grads.append(pen_grad * shape_func)
        pen_hist.append(pen_costs)

        #Temporary!
#        discrepancy_idcs = np.array([0,1,2])

        mean_fid = np.mean(fids)
        if discrepancy_penalty:
#            if discrepancy_idcs is None:
#                discrepancy_idcs = range(len(fids))
#            discrepancies = [f - mean_fid for f in fids[discrepancy_idcs]]
#            discrepancy_cost = discrepancy_penalty * sum(df**2 for df in discrepancies)
#            d_discrepancy_cost = 2 * discrepancy_penalty * sum(df * d_fid for df, d_fid in zip(discrepancies, fid_grads[discrepancy_idcs]))
            discrepancies = [f - mean_fid for f in fids]
            discrepancy_cost = discrepancy_penalty * sum(df**2 for df in discrepancies)
            d_discrepancy_cost = 2 * discrepancy_penalty * sum(df * d_fid for df, d_fid in zip(discrepancies, fid_grads))
  
            pen_costs.append(discrepancy_cost)
            pen_grads.append(d_discrepancy_cost)

        aux_fid_grads = aux_precon * np.array(aux_fid_grads)
        tot_cost = (1 - mean_fid) + sum(pen_costs)
        tot_grad = -np.mean(fid_grads, axis=0) + sum(pen_grads)
        tot_grad = np.concatenate((tot_grad.flatten(), -np.mean(aux_fid_grads, axis=0)))

        global N_ITER
        report_data = dict(
            n_iter=N_ITER,
            sim_controls=controls,
            aux_params=aux_params,
            dt=dt,
            n_ss=n_ss,
            raw_controls=raw_controls,
            awg_controls=awg_controls,
            full_controls=full_controls,
            shape_func=shape_func,
            response=response,
            setups=setups,
            props=props,
            fids=np.array(fids),
            fids_hist=fids_hist,
            fid_grads=np.array(fid_grads),
            aux_fid_grads=np.array(aux_fid_grads),
            pen_costs=pen_costs,
            pen_grads=pen_grads,
            pen_hist=pen_hist,
            tot_cost=tot_cost,
            tot_grad=tot_grad,
            outdir=outdir,
        )

        for fn in reporter_fns:
            fn(force=force_report, **report_data)

        if save_data and not N_ITER % save_data:
            print('Saving data...')
            save_report_data(report_data, outdir)
        N_ITER += 1

        return report_data

    def _cost_function(controls):
        data = get_report_data(controls)
        if term_fid is not None and data['fids'][0] >= term_fid:
            raise OptFinishedException('Requested fidelity obtained', controls)
        global N_ITER
        if check_grad and N_ITER % check_grad == 0:
            print('Checking gradient...')
            d_controls = np.zeros_like(controls)
            i = np.random.randint(0, len(d_controls))
            d_controls[i] = 1e-7
            data2 = get_report_data(controls + d_controls)
            g1 = data['tot_grad'][i]
            g2 = 1e7*(data2['tot_cost'] - data['tot_cost'])
            print('Calculated Gradient:', g1, 'Estimated Gradient:', g2)
            if g1/g2 < .99 or g1/g2 > 1.01:
                print('WARNING: Calculated gradient is far from estimated gradient (ratio = %s)' % (g1 / g2))
        return data['tot_cost'], data['tot_grad']

    cost_function = _cost_function
    get_controls = lambda x: x
    init_params = np.concatenate((init_controls.flatten(), init_aux_params))

    if freq_range is not None:
        min_freq, max_freq = freq_range
        freqs = np.fft.fftshift(np.fft.fftfreq(plen, dt))
        fft_lpad = np.argwhere(freqs > min_freq)[0,0]
        fft_rpad = np.argwhere(freqs[::-1] < max_freq)[0,0]
        assert fft_lpad > 0
        assert fft_rpad > 0
        c_init_controls = init_controls[::2] + 1j*init_controls[1::2]
        init_params = np.fft.fftshift(np.fft.fft(c_init_controls), axes=1)[:,fft_lpad:-fft_rpad]
        fft_size = init_params.shape[1]
        init_params = np.array([init_params.real, init_params.imag]).flatten()

        def get_controls(fft_controls):
            r_fft_ctrls, i_fft_ctrls = fft_controls.reshape([2, -1, fft_size])
            fft = r_fft_ctrls + 1j*i_fft_ctrls
            nc = fft.shape[0]
            fft = np.fft.fftshift(np.hstack([
                np.zeros((nc, fft_lpad)), fft, np.zeros((nc, fft_rpad))
            ]), axes=(1,))
            c_controls = np.fft.ifft(fft)
            return np.array([c_controls.real, c_controls.imag]).transpose(1, 0, 2).flatten()

        def fft_cost_func(fft_controls):
            controls = get_controls(fft_controls)
            c, dc = _cost_function(controls)
            dc = dc.reshape((-1, plen))
            c_dc = dc[::2] - 1j*dc[1::2]
            dc_dfft = np.fft.fftshift(np.fft.ifft(c_dc), axes=(1,))[:,fft_lpad:-fft_rpad].conj()
            return c, np.array([dc_dfft.real, dc_dfft.imag]).flatten()

        cost_function = fft_cost_func


    if test_cost:
        import time
        c1, g1 = cost_function(init_params)
        t_tot = 0
        for _ in range(test_cost):
            d_controls = np.zeros_like(init_params)
            i = np.random.randint(0, len(d_controls))
            d_controls[i] = 1e-7
            t0 = time.time()
            c2, _ = cost_function(init_params + d_controls)
            t1 = time.time()
            t_tot += t1 - t0
            print(i, (c2 - c1) / 1e-7, g1[i], 1 / (1e-7*g1[i] / (c2 - c1)))
        a_time = t_tot / test_cost
        print('Average time:', end=' ')
        if a_time > 1:
            print(a_time, 'sec')
        elif a_time > 1e-3:
            print(a_time * 1e3, 'msec')
        else:
            print(a_time * 1e6, 'usec')
        return

    data = get_report_data(get_controls(init_params))
    opt_result = None
    if not eval_once:
        try:
            opt_result = minimize(cost_function, init_params, jac=True, method='L-BFGS-B', options=opts)
            x = opt_result.x
        except OptFinishedException as e:
            x = e.controls
            opt_result = OptimizeResult(
                message='desired fidelity reached', success=True, status=0, nfev=N_ITER, nit=N_ITER,
            )
        data = get_report_data(x, force_report=True)
    return GrapeResults(data, opt_result)

def save_report_data(data, outdir=None, parent=None):
    import h5py
    close_after = False
    if parent is None:
        close_after = True
        path = 'report_data.h5'
        if outdir is not None:
            os.path.join(outdir, path)
        parent = h5py.File(path, 'w')
    for k, v in list(data.items()):
        if isinstance(v, dict):
            g = parent.create_group(k)
            save_report_data(v, parent=g)
        elif isinstance(v, (list, np.ndarray)):
            arr = np.array(v)
            # print k, arr.dtype
            if arr.dtype != np.object_ and arr.size:
                parent[k] = v
        elif isinstance(v, (int, float, str)):
            parent.attrs[k] = v
        else:
            pass
            # print "Can't save data %s of type: %s" % (k, type(v))
    if close_after:
        parent.close()


def scan_plen(start, stop, step, setups, penalties, reporters, **kwargs):
    best_val = float('inf')
    for plen in range(start, stop, step):
        print('Using PLEN=%d' % plen)
        init_ctrls = random_waves(4, plen)
        data, ret = run_grape(init_ctrls, setups, penalties, reporters, **kwargs)
        if ret.fun < best_val:
            best_val = ret.fun
            best_ctrls = ret.x.reshape((-1, plen))
    return best_ctrls


if __name__ == '__main__':
    n_ctrls = 6
    dim = 30
    plen = 200
    n_states = 2
    from .setups import StateTransferSetup

    def random_hermitian():
        H = np.random.randn(dim, dim) + 1j*np.random.randn(dim, dim)
        return H + H.conj().T

    H0 = random_hermitian()
    Hcs = np.array([random_hermitian() for _ in range(n_ctrls)])
    inits = eigh(random_hermitian())[1][:, :n_states].T
    finals = eigh(random_hermitian())[1][:, :n_states].T
    setups = [StateTransferSetup(H0, Hcs, inits, finals)]
    init_ctrls = np.random.randn(n_ctrls, plen)
    # filt_func = lambda f: 1 / np.sqrt(1 + (f / .05)**2)
    # resp = get_impulse_response(plen, 1, filt_func)
    run_grape(init_ctrls, setups, test_cost=10, freq_range=(-.1, .1))
