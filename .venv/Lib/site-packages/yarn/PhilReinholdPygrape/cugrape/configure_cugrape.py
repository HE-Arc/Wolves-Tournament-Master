import os
from collections import namedtuple, Counter
import sympy
import subprocess
import numpy as np
from pygrape.cugrape.normal_order import AnnihilateMode, CreateMode, NMode, anti_normal_order, dagger

ModeTerm = namedtuple('ModeTerm', 'n n_ad n_a')

def get_pow(op):
    if op == 1:
        return 0
    elif isinstance(op, sympy.Pow):
        return op.args[1]
    else:
        return 1

def get_terms(H, n_modes, n_left=None):
    H = anti_normal_order(H)
    if n_left is None:
        n_left = n_modes
    rops = H.atoms(AnnihilateMode, CreateMode)
    terms = []

    if n_left > 0:
        d = sympy.collect(H, (CreateMode(n_left-1), AnnihilateMode(n_left-1)), evaluate=False)
        for k, v in sorted(d.items(), key=repr):
            kpow = get_pow(k)
            if isinstance(k, AnnihilateMode):
                kpow *= -1
            for op_pows, polys in get_terms(v, n_modes, n_left-1):
                terms.append((op_pows + (kpow,), polys))

    else:
        terms = [((), get_poly(H, n_modes))]

    return terms


def get_poly(H, n_modes):
    terms = [H]

    if isinstance(H, sympy.Add):
        terms = H.args

    def get_poly_term(t):
        c, nc = t.args_cnc()
        c = np.product(c)
        mode_pows = [0]*n_modes
        for subterm in nc:
            st_pow = 1
            if isinstance(subterm, sympy.Pow):
                st_pow = subterm.args[1]
                subterm = subterm.args[0]
            assert isinstance(subterm, NMode), (subterm, t)
            mode_pows[subterm.args[0]] += st_pow
        return (-1j*complex(c), mode_pows)

    return list(map(get_poly_term, terms))


def get_hmt_ops(n_modes, mode_dims=None, numeric=False):
    if not numeric:
        return [(AnnihilateMode(n), CreateMode(n)) for n in range(n_modes)]

    assert mode_dims is not None

    def q_destroy(n):
        import qutip as q
        ops = [q.qeye(d) for d in mode_dims]
        ops[n] = q.destroy(mode_dims[n])
        return q.tensor(*list(reversed(ops)))

    ops = map(q_destroy, range(n_modes))
    return [(a, a.dag()) for a in ops]

def get_lindblad_hmt_ops(n_modes, mode_dims=None, **kwargs):
    mode_dims = np.tile(mode_dims,2) 
    aads = get_hmt_ops(n_modes*2, mode_dims=mode_dims, **kwargs)
    return aads[n_modes:], aads[:n_modes]
    #using the second half makes L = IoH - H^ToI simpler.
    
def write_if_different(fname, text):
    if not(os.path.exists(fname)) or open(fname, 'r').read() != text:
        open(fname, 'w').write(text)


def configure(mode_dims_variants, Hs, plen, nstate, taylor_order, double=True):
    all_Hts, Hcs = [], {'noct':[], 'withct':[]}
    nt = 0
    tot_dims = [np.product(mode_dims) for mode_dims in mode_dims_variants]
    n_modes = len(mode_dims_variants[0])
    for H in Hs:
        Hcs['noct'].append(get_terms(H, n_modes))
        Hcs['withct'].append(get_terms(dagger(H), n_modes))

    assert all(len(x) == n_modes for x in mode_dims_variants), mode_dims_variants
    cplx_size = 16 if double else 8
    use_double_buffer = [ 4 * cplx_size * dim <= 0xc000 for dim in tot_dims ]
    print('Double Buffer?', use_double_buffer)

    hdata = dict(
        mode_dims_variants=mode_dims_variants,
        tot_dims=tot_dims,
        n_modes=n_modes,
        n_add_steps=[int(np.ceil(np.log2(d))) for d in tot_dims],
        Hcs=Hcs,
        double=double,
        use_double_buffer=use_double_buffer
    )

    cudir = os.path.dirname(os.path.abspath(__file__))
    from jinja2 import Environment, FileSystemLoader, StrictUndefined
    loader = FileSystemLoader(cudir)
    env = Environment(loader=loader, undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('hmatvec.jinja2')
    out_fn = os.path.join(cudir, 'kernel.cu')
    write_if_different(out_fn, template.render(hdata))

    nctrls = len(Hs) - 1

    dfns = dict(
        NCTRLS=nctrls, NTERMS=len(all_Hts),
        PLEN=plen, NSTATE=nstate,
        MAXNNZ=2, TAYLOR_ORDER=taylor_order,
        NVAR=len(mode_dims_variants),
    )
    cpp_definitions = ['#define {} {}'.format(k, v) for k, v in sorted(dfns.items())]
    cpp_definitions.append('typedef {} R;'.format('double' if double else 'float'))
    cpp_definitions = '\n'.join(cpp_definitions)
    path = os.path.join(os.path.dirname(__file__), 'cugrape')
    prev_cwd = os.getcwd()
    os.chdir(cudir)
    try:
        write_if_different("constants.h", cpp_definitions)
        import sys
        if sys.platform == 'win32':        
            subprocess.check_call('build_windows.bat', cwd=cudir)
        else:
            subprocess.check_call('make')
    finally:
        os.chdir(prev_cwd)


if __name__ == '__main__':
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

    mode_dims = [[2, 10, 10]]
    Hs = [H0, Hxq, Hyq, Hx1, Hy1, Hx2, Hy2]
    configure(mode_dims, Hs, 300, 1, 20)

