"""
Determine the optimal taylor parameters for computing the action of the matrix exponential
See: Al-Mohy & Higham (2011)
http://epubs.siam.org/doi/abs/10.1137/100788860
"""
import os
import numpy as np
import sympy

from joblib.memory import Memory
# mem = Memory(cachedir=os.path.dirname(__file__))
mem = Memory(cachedir=os.path.join(os.path.expanduser("~"), '.joblib-cache'))

def make_hm(m, n_max):
    from sympy.abc import x
    tm = sympy.exp(x).series(x, 0, m+1).removeO()
    expr = sympy.log(sympy.exp(-x) * tm)
    p1 = sympy.Poly(expr.series(x, 0, n_max).removeO())
    return sympy.Poly.from_list([abs(ck) for ck in p1.all_coeffs()], x)

@mem.cache
def theta_m(m, tol, n_max):
    from sympy.abc import x
    hm = make_hm(m, n_max)
    d_hm = hm.diff(x)

    def f(x):
        return hm(x) - x*tol

    def fp(x):
        return d_hm(x) - tol

    from scipy.optimize import newton
    xmin = newton(f, 20, fprime=fp, maxiter=300, tol=1e-13)
    return float(xmin)

def get_taylor_params(Anorm, tol, m_max=40):
    ms = np.arange(1, m_max+1)
    thetas = np.array([theta_m(m, tol, max(2*m, 6)) for m in ms])
    i_opt = np.argmin(ms * np.ceil(Anorm / thetas))
    m_opt = ms[i_opt]
    s_opt = int(np.ceil(Anorm / thetas[i_opt]))
    return m_opt, s_opt


if __name__ == '__main__':
    print([get_taylor_params(anorm, 1e-2, 50) for anorm in np.linspace(0.1, 1.5, 15)])
    print([get_taylor_params(anorm, 1e-9, 50) for anorm in np.linspace(0.1, 1.5, 15)])
