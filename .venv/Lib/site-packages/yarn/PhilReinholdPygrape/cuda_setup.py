import numpy as np
from .setups import StateTransferSetup
from .cugrape.configure_cugrape import get_hmt_ops
import os
import subprocess


class CudaStateTransferSetup(object):
    def __init__(self, mode_dims, H0, Hcs, inits, finals, taylor_order=10, use_double=False):
        self.H0 = H0
        self.Hcs = Hcs
        self.inits = inits
        self.finals = finals
        self.mode_dims = mode_dims
        if isinstance(self.mode_dims[0], int):
            self.mode_dims = [self.mode_dims]
            self.inits = [self.inits]
            self.finals = [self.finals]
        self.inits = list(map(np.array, self.inits))
        self.finals = list(map(np.array, self.finals))
        self.taylor_order = taylor_order
        self.use_double = use_double
        self.cugrape = None

    def get_fids(self, controls, aux_params, dt):
        if self.cugrape is None:
            nctrls, plen = controls.shape
            assert len(self.Hcs) == nctrls
            self.init_cugrape(plen, dt)

        nstate = len(self.inits[0])
        ovlp, d_ovlps = self.cugrape.grape_step(controls.T)
        fid = abs(ovlp/nstate)
        d_fid = (ovlp.real[:,None,None]*d_ovlps.real + ovlp.imag[:,None,None]*d_ovlps.imag) / abs(ovlp[:,None,None]) / nstate
        return None, fid, d_fid.transpose(0,2,1), np.zeros((len(fid), 0))

    def init_cugrape(self, plen, dt):
        from .cugrape.configure_cugrape import configure
        Hs = [self.H0] + list(self.Hcs)
        Hs = [dt*H for H in Hs]
        nstate = len(self.inits[0])
        configure(self.mode_dims, Hs, plen, nstate, self.taylor_order, self.use_double)
        from .cugrape import cugrape
        from six.moves import reload_module
        self.cugrape = reload_module(cugrape)

        cugrape.init_gpu_memory()
        for i, (mds, psi0, psif) in enumerate(zip(self.mode_dims, self.inits, self.finals)):
            print(mds, np.product(mds), psi0.shape, psif.shape)
            dim = psi0.shape[1]
            assert psi0.shape == (nstate, dim)
            assert psif.shape == (nstate, dim)
            assert np.product(mds) == dim
            cugrape.load_states(i, psi0, psif)
