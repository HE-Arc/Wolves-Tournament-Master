import itertools
import numpy as np
import qutip as q
from . import StateTransferSetup, LindbladSetup, SubspaceSetup

CONFIG = dict(
    c_levels=25,
    q_levels=3,
    n_bits=3,
    selected_bit=0,
    alpha=np.sqrt(3),
    n_qubits=3,
    chi=-1.968e-3,
    chi_prime=-1.496e-5,
    kerr=-3.15e-6,
    anharm=-262e-3,
    qdrive=17.95e-3,
    cdrive=34.1e-3,
    T1q=110e3,
    T2eq=40e3,
    T1cav=2.8e6,
    impulse_fname=r'C:\data\impulses\fit_impulse_20160122165605.npz',
    impulse_data=0.5 * np.ones(2),
    n_ss=2,
    dt=2,
    amp_threshold=.72,
    amp_penalty=5e-5,
    deriv_penalty=1e-4,
    discrepancy_penalty=1e3,
    init_norm=1e-2,
    init_n_pts=5,
    pulse_dir=r'C:\data\pulses',
    eval_once=False,
    report_interval=10,
    check_grad=25,
    term_fid=.9995,
    solver_opts={},
    op_kwargs={},
    init_fname=None,
    print_costs=True,
    save_data=True,
    verify_from_setup=False,
    reporters=[],
    penalties=[],
)


def kron(first, *rest):
    r = first
    for a in rest:
        r = np.kron(r, a)
    return r


class Mode(object):
    def __init__(self, modes_levels, idx):
        op_list = [q.qeye(n) for n in modes_levels]
        op_list[idx] = q.destroy(modes_levels[idx])
        self.levels = modes_levels[idx]
        self.a = q.tensor(*op_list)
        self.ad = self.a.dag()
        self.n = self.ad * self.a
        self.x = self.ad + self.a
        self.y = 1j*(self.a - self.ad)

    def basis(self, n):
        return q.basis(self.levels, n)


class Operation(object):
    def __init__(self, modes_levels):
        self.name = type(self).__name__
        self.modes_levels = modes_levels
        self.modes = [Mode(modes_levels, i) for i in range(len(modes_levels))]
        self.H0_terms = []
        self.Hcs = []
        self.c_ops = []
        self.wave_names = []
        self.inits = []
        self.finals = []
        self.coherent_tx = True
        self.loss_vec = None

    def make_setup(self, H0_weights=None, Hc_weights=None, taylor=False, subspace=False, lindblad=False):
        if H0_weights is None:
            H0_weights = [1]*len(self.H0_terms)
        if Hc_weights is None:
            Hc_weights = [1]*len(self.Hcs)
        H0 = sum(w*H for w, H in zip(H0_weights, self.H0_terms))
        Hcs = [w*H for w, H in zip(Hc_weights, self.Hcs)]
        if lindblad:
            return LindbladSetup(H0, Hcs, self.inits, self.finals, self.c_ops, use_taylor=taylor, sparse=True)
        if subspace:
            return SubspaceSetup(H0, Hcs, self.inits, self.finals, self.c_ops)
        return StateTransferSetup(
            H0, Hcs, self.inits, self.finals, c_ops=self.c_ops,
            coherent=self.coherent_tx, loss_vec=self.loss_vec, use_taylor=taylor
        )

    def basis(self, *ns):
        return q.tensor(*[q.basis(N, n) for N, n in zip(self.modes_levels, ns)])

    def add_detune(self, detune, idx):
        self.H0_terms.append(2*np.pi*detune * self.modes[idx].n)

    def add_anharm(self, anharm, idx):
        a, ad = self.modes[idx].a, self.modes[idx].ad
        self.H0_terms.append(np.pi*anharm * (ad*ad*a*a))

    def add_chi(self, chi, i1=0, i2=1):
        if i1 == i2:
            return self.add_anharm(chi, i1)
        m1, m2 = self.modes[i1], self.modes[i2]
        self.H0_terms.append(2*np.pi*chi * (m1.n*m2.n))

    def add_chi_prime(self, chi_p, i1=1, i2=0):
        m1, m2 = self.modes[i1], self.modes[i2]
        self.H0_terms.append(np.pi*chi_p * (m1.n * m2.n * (m2.n - 1)))

    def add_t1(self, t1, idx):
        self.c_ops.append(np.sqrt(1./t1) * self.modes[idx].a)

    def add_t2(self, t2, idx):
        self.c_ops.append(np.sqrt(1./t2) * self.modes[idx].n)

    def add_iq_drives(self, drive, idx):
        m = self.modes[idx]
        self.Hcs.extend([2*np.pi*drive*m.x, 2*np.pi*drive*m.y])
        self.wave_names.extend(['X%d' % idx, 'Y%d'%idx])



class MultiCavMultiQubitOp(Operation):
    def __init__(self, n_qubits=None, n_cavs=None, c_levels=None, q_levels=None):
        if n_qubits is None:
            n_qubits = CONFIG['n_qubits']
        if n_cavs is None:
            n_cavs = CONFIG['n_cavs']
        if c_levels is None:
            c_levels = CONFIG['c_levels']
        if q_levels is None:
            q_levels = CONFIG['q_levels']
        self.n_qubits = n_qubits
        self.n_cavs = n_cavs
        self.c_levels = c_levels
        self.q_levels = q_levels
        super(MultiCavMultiQubitOp, self).__init__([c_levels]*n_cavs + [q_levels]*n_qubits)
        self.cavs = self.modes[:n_cavs]
        self.qubits = self.modes[n_cavs:]
        cav_vecs = [[1]*(c_levels - 1) + [0] for _ in range(n_cavs)]
        qubit_vecs = [[1]*q_levels for _ in range(n_qubits)]
        self.loss_vec = kron(*(cav_vecs + qubit_vecs))


class CavityQubitOp(MultiCavMultiQubitOp):
    def __init__(self, c_levels=None, q_levels=None):
        super(CavityQubitOp, self).__init__(1, 1, c_levels, q_levels)
        self.cav = self.cavs[0]
        self.qubit = self.qubits[0]

    def g_state(self, n):
        return self.with_qubit(self.cav.basis(n), 0)

    def e_state(self, n):
        return self.with_qubit(self.cav.basis(n), 1)

    def with_qubit(self, cav_state, nq):
        return q.tensor(cav_state, self.qubit.basis(nq))

    def coherent(self, alpha, nq=0):
        return self.with_qubit(q.coherent(self.c_levels, alpha), nq)

    def cat(self, alpha, phi=0, nq=0):
        c1 = self.coherent(alpha, nq)
        c2 = self.coherent(-alpha, nq)
        return (c1 + np.exp(1j*phi)*c2).unit()



class SwapPhotonStatesOp(CavityQubitOp):
    def __init__(self, n0, n1=0, c_levels=None, q_levels=None):
        super(SwapPhotonStatesOp, self).__init__(c_levels, q_levels)
        self.name += str(n0)
        self.name += str(n1)
        self.inits = [self.basis(n0, 0), self.basis(n1, 0)]
        self.finals = [self.basis(n1, 0), self.basis(n0, 0)]


class QcmapOp(CavityQubitOp):
    def __init__(self, alpha=None, c_levels=None, q_levels=None):
        super(QcmapOp, self).__init__(c_levels, q_levels)
        if alpha is None:
            alpha = CONFIG['alpha']
        self.name += '%.2f' % alpha
        self.inits = [self.basis(0, 0), self.basis(0, 1)]
        self.finals = [self.cat(alpha), self.cat(1j*alpha)]


class CavityRegisterOp(CavityQubitOp):
    def __init__(self, n_bits=None, c_levels=None, q_levels=None):
        super(CavityRegisterOp, self).__init__(c_levels, q_levels)
        if n_bits is None:
            n_bits = CONFIG['n_bits']
        self.name += str(n_bits)
        assert self.c_levels >= 2**n_bits, (c_levels, n_bits)
        self.n_bits = n_bits
        self.g_states = self.basis_states(0)
        self.e_states = self.basis_states(1)

    def basis_states(self, q_level=0):
        d = {}
        for i, bits in enumerate(itertools.product(range(2), repeat=self.n_bits)):
            d[bits] =  self.basis(i, q_level)
        return d


class FlipParityOp(CavityRegisterOp):
    def __init__(self, flip_bit=None, n_bits=None, c_levels=None, q_levels=None):
        super(FlipParityOp, self).__init__(n_bits, c_levels, q_levels)
        if flip_bit is None:
            flip_bit = CONFIG['selected_bit']
        self.name += str(flip_bit)
        for bits, init in self.g_states.items():
            f_bits = tuple((1-b) if i == flip_bit else b for i, b in enumerate(bits))
            self.inits.append(init)
            self.finals.append(self.g_states[f_bits])


class MeasureParity(CavityRegisterOp):
    def __init__(self, meas_bit=None, n_bits=None, c_levels=None, q_levels=None, invert=False):
        super(MeasureParity, self).__init__(n_bits, c_levels, q_levels)
        self.coherent_tx = False
        if meas_bit is None:
            meas_bit = CONFIG['selected_bit']
        self.name += str(meas_bit)
        states0, states1 = self.g_states, self.e_states
        if invert:
            states0, states1 = states1, states0
        for bits, init in self.g_states.items():
            self.inits.append(init)
            if bits[meas_bit]:
                self.finals.append(states1[bits])
            else:
                self.finals.append(states0[bits])


class MultiQubitOp(MultiCavMultiQubitOp):
    def __init__(self, n_qubits=None, q_levels=None):
        super(MultiQubitOp, self).__init__(0, n_qubits, 0, q_levels)


class MultiQubitCavityOp(MultiCavMultiQubitOp):
    def __init__(self, n_qubits=None, c_levels=None, q_levels=None):
        super(MultiQubitCavityOp, self).__init__(1, n_qubits, c_levels, q_levels)
        self.cav = self.cavs[0]


class LogicalCavityQubitOp(CavityQubitOp):
    def __init__(self, **kwargs):
        super(LogicalCavityQubitOp, self).__init__(**kwargs)
        self.logical_states = self.make_logicals()
        self.g_logicals = [self.with_qubit(s, 0) for s in self.logical_states]
        self.e_logicals = [self.with_qubit(s, 1) for s in self.logical_states]
        self.error_ops = self.make_error_ops()
        self.g_error_states, self.e_error_states = self.make_error_states()

    def make_logicals(self):
        raise NotImplementedError

    def make_error_ops(self):
        return []

    def make_error_states(self):
        ret_g, ret_e = [], []
        for op in self.error_ops:
            ret_g.append([])
            ret_e.append([])
            for state in self.g_logicals:
                ret_g[-1].append((op * state).unit())
            for state in self.e_logicals:
                ret_e[-1].append((op * state).unit())
        return ret_g, ret_e


class FockEncoding(LogicalCavityQubitOp):
    def make_logicals(self):
        return [self.cav.basis(0), self.cav.basis(1)]


class KittenCodeOp(LogicalCavityQubitOp):
    def make_logicals(self):
        return [
            self.cav.basis(2),
            (self.cav.basis(0) + self.cav.basis(4)).unit(),
        ]

    def make_error_ops(self):
        return [self.cav.a]


class LogicalEncode(LogicalCavityQubitOp):
    def __init__(self, **kwargs):
        super(LogicalEncode, self).__init__(**kwargs)
        self.inits = [self.g_state(0), self.e_state(0)]
        self.finals = [self.g_logicals[0], self.g_logicals[1]]


class LogicalDecode(LogicalEncode):
    def __init__(self, **kwargs):
        super(LogicalDecode, self).__init__(**kwargs)
        self.inits, self.finals = self.finals, self.inits


class ErrorDetect(LogicalCavityQubitOp):
    def __init__(self, n_error=0, **kwargs):
        super(ErrorDetect, self).__init__(**kwargs)
        self.inits = self.g_logicals + self.g_error_states[n_error]
        self.finals = self.g_logicals + self.e_error_states[n_error]


class ErrorCorrect(LogicalCavityQubitOp):
    def __init__(self, n_error=0, **kwargs):
        super(ErrorDetect, self).__init__(**kwargs)
        self.inits = self.g_error_states[n_error]
        self.finals = self.g_logicals


class LogicalOperation(LogicalCavityQubitOp):
    def __init__(self, U, **kwargs):
        super(LogicalOperation, self).__init__(**kwargs)
        self.inits = self.g_logicals
        self.finals = [
            U[0,0]*self.g_logicals[0] + U[1,0]*self.g_logicals[1],
            U[1,0]*self.g_logicals[0] + U[1,1]*self.g_logicals[1],
        ]


def make_op(cls0, cls1, **kwargs):
    class CombinedOp(cls0, cls1):
        pass
    return CombinedOp(**kwargs)


def run_operation(cls, pulse_len, **kwargs):
    def get(name):
        return kwargs.get(name, CONFIG[name])

    for k in kwargs:
        assert k in CONFIG, ('Unknown option %s' % k)

    NC = get('c_levels')
    NQ = get('q_levels')
    op_kwargs = get('op_kwargs')
    ops = [cls(c_levels=NC+x, q_levels=NQ, **op_kwargs) for x in (0, 1, 2, 3)]
    setups = []

    for op in ops:
        op.add_chi(get('chi'), 0, 1)
        op.add_chi_prime(get('chi_prime'), 1, 0)
        op.add_anharm(get('kerr'), 0)
        op.add_anharm(get('anharm'), 1)
        op.add_iq_drives(get('cdrive'), 0)
        op.add_iq_drives(get('qdrive'), 1)
        setups.append(op.make_setup())

    setups, test_setup = setups[:-1], setups[-1]

    impulse_1ns = None
    impulse_fname = get('impulse_fname')
    if impulse_fname is not None:
        data = np.load(impulse_fname)
        impulse_1ns = np.array([data['ys1ns'], data['ys1ns']])

    from pygrape import run_grape, random_waves
    from pygrape import make_amp_cost, make_lin_deriv_cost, make_tail_cost
    from pygrape import print_costs, plot_waves, plot_fidelity, save_waves, plot_states, verify_from_setup
    penalties = [x for x in get('penalties')]
    if get('amp_penalty'):
        penalties.append(make_amp_cost(get('amp_penalty'), get('amp_threshold'), iq_pairs=True))
    if get('deriv_penalty'):
        penalties.append(make_lin_deriv_cost(get('deriv_penalty')))

    wave_names = 'cI', 'cQ', 'qI', 'qQ'
    RI = get('report_interval')
    reporters = [x for x in get('reporters')]
    if get('print_costs'):
        reporters.append(print_costs())
    if get('save_data'):
        reporters.extend([
            save_waves(wave_names, RI),
            plot_waves(wave_names, RI),
            plot_fidelity(RI),
            plot_states(RI),
        ])
    if get('verify_from_setup'):
        reporters.append(verify_from_setup(test_setup, RI))

    init_fname = get('init_fname')
    if init_fname is not None:
        d = np.load(init_fname)
        init_ctrls = [d['raw_'+name] for name in wave_names]
    else:
        init_ctrls = get('init_norm') * random_waves(4, pulse_len, get('init_n_pts'))

    import os
    outdir = os.path.join(get('pulse_dir'), ops[0].name)

    return run_grape(
        init_ctrls, setups, penalties, reporters, outdir,
        maxcor=20, n_proc=len(setups), n_ss=get('n_ss'), dt=get('dt'), response=impulse_1ns,
        save_data=get('save_data')*RI, impulse_data=get('impulse_data'),
        check_grad=get('check_grad'), term_fid=get('term_fid'),
        discrepancy_penalty=get('discrepancy_penalty'), eval_once=get('eval_once'), **get('solver_opts')
    )

