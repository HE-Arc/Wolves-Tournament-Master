#!/usr/bin/env python -W ignore::DeprecationWarning

from __future__ import print_function
import inspect
from math import pi, sqrt, factorial
import qutip
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches as mpatches
from matplotlib.gridspec import GridSpec
from os import path
from scipy.special import genlaguerre
from scipy.linalg import svd, expm
from scipy.optimize import brute
from scipy import signal
from mpl_toolkits.axes_grid1 import ImageGrid
import shutil

import warnings
warnings.filterwarnings("ignore")

__all__ = [
    'Reporter', 'print_costs', 'print_grads', 'save_waves', 'plot_waves',
    'save_script', 'liveplot_waves', 'liveplot_prop', 'plot_fidelity', 'plot_unitary', 'plot_cwigs',
    'verify_from_setup', 'verify_master_equation', 'plot_matrix', 'plot_states',
    'verify_sensitivity', 'verify_dispersion_sensitivity', 'verify_with_response',
    'set_output_fmt', 'plot_penalties', 'plot_trajectories', 'cutoff'
]


def run_reporter(fn, data):
    args = [data[k] for k in inspect.getargspec(fn).args if k != 'self']
    fn(*args)


OUTPUT_FMT = 'pdf'
def set_output_fmt(fmt):
    """
    Set the file suffix used for matplotlib.savefig. By default this is pdf
    """
    global OUTPUT_FMT
    OUTPUT_FMT = fmt


class Reporter(object):
    """
    Base reporter class. Subclass and implement run method to use

    Parameters
    ----------
    spacing : int
        Number of iterations to perform between evaluations of this reporter
    """
    def __init__(self, spacing=1):
        self.spacing = spacing
        self.n_call = 0

    def __call__(self, force=False, **kwargs):
        if force or self.n_call % self.spacing == 0:
            args = [kwargs[k] for k in inspect.getargspec(self.run).args[1:]]
            self.run(*args)
        self.n_call += 1

    def run(self, *args):
        raise NotImplementedError


class print_costs(Reporter):
    """
    Prints the current fidelity from each setup, and the cost from each penalty
    """
#    TODO:  Replace this with a Logging solution for better support of
#           multiprocessing in Spyder (which dosn't let children print
#           to STDOUT)

    def run(self, fids, pen_costs, n_iter):
        print(n_iter, '- Fids:', end=' ')
        print(' '.join(['%.7g' % c for c in fids]), end=' ')
        if len(pen_costs):
            print('Penalties:', end=' ')
            print(' '.join(['%.7g' % c for c in pen_costs]))
    

class cutoff(Reporter):
    """
    Raise exception is we go too many rounds without going over a threshold
    """

    def __init__(self, cut_rounds=10, cut_fid=.715):
        super(cutoff, self).__init__()
        self.cut_rounds = cut_rounds
        self.cut_fid = cut_fid
        
    def run(self, fids, pen_costs, n_iter):
        if np.mean(fids) < self.cut_fid and n_iter>self.cut_rounds:
            txt = 'Failed to get fid > %.3f in %d rounds' % (self.cut_fid, self.cut_rounds)
            raise Exception(txt)
    
    
class print_grads(Reporter):
    """
    Prints the maximum gradient value for both the control and auxiliary parameters
    """
    def run(self, fid_grads, aux_fid_grads):
        print('Max Fid Grad:', abs(fid_grads).max(), end=' ')
        if aux_fid_grads.size:
            print('Max Aux Grad:', abs(aux_fid_grads).max())
        else:
            print('')


class save_waves(Reporter):
    """
    Saves the controls in a .npz file. To retrieve the data, use
    ``np.load('waves.npz')``, which returns a dictionary-like object.

    Parameters
    ----------
    wave_names : List of str
        Names of the controls when saved in dictionary. There should be
        N_CTRLS entries in this list.
    """
    def __init__(self, wave_names, spacing):
        super(save_waves, self).__init__(spacing)
        self.wave_names = wave_names

    def run(self, outdir, sim_controls, dt, n_ss, raw_controls, shape_func, response, tot_cost):
        print('saving...')
        wave_dict = {'sim_'+k:w for k, w in zip(self.wave_names, sim_controls)}
        wave_dict.update({'raw_'+k:w for k, w in zip(self.wave_names, raw_controls)})

        if response is not None:
            pad = np.zeros((len(raw_controls), len(response)))
            awg_controls = np.hstack([raw_controls * shape_func, pad])
        else:
            awg_controls = raw_controls * shape_func
        wave_dict.update({k:w for k, w in zip(self.wave_names, awg_controls)})

        wave_dict['sim_dt'] = dt / float(n_ss)
        wave_dict['dt'] = dt
        wave_dict['n_ss'] = n_ss
        wave_dict['response'] = response
        np.savez(path.join(outdir, 'waves.npz'), **wave_dict)


class plot_waves(Reporter):
    """
    Uses matplotlib to plot the current waves, and saves them under
    waves.pdf in the output directory. Since plotting with matplotlib
    can be slow, make sure the spacing is set reasonably so plotting
    does not dominate the execution time.
    """
    def __init__(self, wave_names, spacing=5, iq_pairs=False, last_only=False):
        super(plot_waves, self).__init__(spacing)
        self.wave_names = wave_names
        self.iq_pairs = iq_pairs
        self.last_only = last_only
        n_ax = len(wave_names)
        
        if iq_pairs:

            n_ax //= 2
            self.fft_fig, self.fft_axes = plt.subplots(n_ax, 1)
        else:
            self.fig = plt.figure()
            gs1 = GridSpec(n_ax, 2)
            for i in range(n_ax/2):
                self.fig.add_subplot(gs1[i*2, 0])
                self.fig.add_subplot(gs1[i*2+1, 0])
                self.fig.add_subplot(gs1[i*2:i*2+2, 1])

            self.axes = self.fig.axes
            

    def run(self, outdir, full_controls, dt, n_ss):
        print('Plotting...')
        sim_dt = dt / n_ss

        wave_axes = [ax for idx,ax in enumerate(self.axes) if idx%3 in [0,1]]
        fft_axes =  [ax for idx,ax in enumerate(self.axes) if idx%3 in [2,]]
        
        if 1:
            #for ax_row in self.axes:
            #    for ax in ax_row:
            for ax in self.axes:
                lines = ax.get_lines()
                ax.clear()
                
                nlines = len(lines)
                for idx, line in enumerate(lines):
                    xs = line.get_xdata()
                    ys = line.get_ydata()
                    
                    alpha = (0.5*idx)/nlines + 0.2
                    ax.plot(xs, ys, 'k-', alpha=alpha)
                    
    #        if self.last_only:
    #            for ax in self.axes:
    #                ax.clear()


        if self.iq_pairs:
            for ax, wave in zip(self.axes, full_controls[::2]):
                ax.clear()
                ax.plot(wave, label='I')
            for ax, wave, name in zip(self.axes, full_controls[1::2], self.wave_names):
                ax.plot(wave, label='Q')
                ax.set_ylabel(name)
            c_waves = full_controls[::2] + 1j*full_controls[1::2]
            fft_waves = np.fft.fftshift(abs(np.fft.fft(c_waves, axis=1))**2)
            fft_freqs = 1e3 * np.fft.fftshift(np.fft.fftfreq(c_waves.shape[1], sim_dt))
            for ax, fft in zip(self.fft_axes, fft_waves):
                ax.clear()
                ax.plot(fft_freqs, fft)
                ax.set_xlim(-80, 80)
            self.fft_fig.savefig(path.join(outdir, 'waves_fft.%s' % OUTPUT_FMT))
        else:
            
            for idx, (ax, wave) in enumerate(zip(wave_axes, full_controls)):
                ax.set_yticks(np.linspace(min(int(np.floor(min(wave))), -1),
                                          max(int( np.ceil(max(wave))),  1), 
                                          5))

                if idx != len(self.axes)-1:
                    ax.set_xticks([]) 
                else:
                    ax.set_xticks(range(0, len(wave)+1, 100))

                ax.plot([0, len(wave)], [0,0], 'k--', lw=0.5)  
                ax.set_xlim(0, len(wave))
                ax.plot(wave, 'r-')
                
            for idx, ax in enumerate(fft_axes):
                
                c_waves = full_controls[2*idx] + 1j*full_controls[2*idx+1]
                 
                fft_wave = np.fft.fftshift(abs(np.fft.fft(c_waves))**2)
                fft_freqs = 1e3 * np.fft.fftshift(np.fft.fftfreq(len(c_waves), sim_dt))
               
                start = len(fft_wave) * (0.5 - .1) #p/m 50 MHz
                stop =  len(fft_wave) * (0.5 + .1)
                ax.plot(fft_freqs[start:stop], fft_wave[start:stop], 'r-')
                ax.set_yticklabels([])
                if idx == 0:
                    ax.set_xticklabels([])
                
        for ax, wave_name in zip(wave_axes, self.wave_names):
            ax.set_title(wave_name, x=-0.075, y=0.25)
            
        try:
            self.fig.savefig(path.join(outdir, 'waves.%s' % OUTPUT_FMT))
        except IOError:
            print('*** Unable to save waves fig.  Is it open?')
        


class save_script(Reporter):
    """
    Saves the script calling this function in the output
    directory. Is only ever evaluated once
    """
    def __init__(self, script_name):
        super(save_script, self).__init__()
        self.script_name = script_name
        self.copied = False

    def run(self, outdir):
        if not self.copied:
            shutil.copy(self.script_name, outdir + '/script.py')
            self.copied = True



class liveplot_waves(Reporter):
    """
    Use the liveplot module to plot waves. Requires liveplot to be
    installed and active::

        pip install liveplot
        python -m liveplot
    """
    def __init__(self, wave_names, spacing=1):
        super(liveplot_waves, self).__init__(spacing)
        from liveplot import LivePlotClient
        self.client = LivePlotClient()
        self.client.clear()
        self.wave_names = wave_names

    def run(self, sim_controls, fids):
        for wave, name in zip(sim_controls, self.wave_names):
            self.client.plot_y(name, wave)
        for i, fid in enumerate(fids):
            self.client.append_y('fid%d' % i, fid)
            self.client.append_y('log_infid%d' % i, np.log(1 - fid))

class liveplot_prop(Reporter):
    """
    Use the liveplot module to plot waves. Requires liveplot to be
    installed and active::

        pip install liveplot
        python -m liveplot
    """
    def __init__(self, spacing=1):
        super(liveplot_prop, self).__init__(spacing)
        from liveplot import LivePlotClient
        self.client = LivePlotClient()
        self.client.clear()

    def run(self, props):
        for i, prop in enumerate(props):
            self.client.plot_z('prop%d' % i, abs(prop))



class plot_fidelity(Reporter):
    """
    Plots the progress of the fidelity as a function of iteration
    """
    def __init__(self, spacing=1):
        super(plot_fidelity, self).__init__(spacing)
        self.all_fids = None

    def run(self, outdir, fids):
        n_fids = len(fids)
        if self.all_fids is None:
            self.all_fids = [[] for _ in range(n_fids)]
        f1, ax1 = plt.subplots(1, 1)
        f2, ax2 = plt.subplots(1, 1)
        for fid_list, fid in zip(self.all_fids, fids):
            fid_list.append(fid)
            ax1.plot(range(len(fid_list)), fid_list, 's-')
            ax2.plot(range(len(fid_list)),1 - np.array(fid_list), 's-')
        ax2.set_yscale('log')
        try:
            f1.savefig(path.join(outdir, 'fidelity.%s' % OUTPUT_FMT))
            f2.savefig(path.join(outdir, 'infidelity.%s' % OUTPUT_FMT))
        except IOError:
            print('*** Figure saving failed, is the pdf open elsewhere?')
        plt.close(f1)
        plt.close(f2)


class plot_penalties(Reporter):
    """
    Plots the progress of the fidelity as a function of iteration
    """
    def __init__(self, spacing=1):
        super(plot_penalties, self).__init__(spacing)

    def run(self, outdir, pen_hist):
        if len(pen_hist) == 0:
            return
        pen_hist = np.array(pen_hist)
        f, axes = plt.subplots(pen_hist.shape[1], 1)
        for ax, pens in zip(axes, pen_hist.T):
            ax.plot(pens)
        f.savefig(path.join(outdir, 'penalties.%s' % OUTPUT_FMT))
        plt.close(f)


class plot_unitary(Reporter):
    def run(self, outdir, setups, props, fids, **kwargs):
        U_target = setups[0].U_target
        U_total = props[0]
        fid = fids[0]
        if U_target.shape[0] != U_target.shape[1]:
            U_target = U_target.T
        f, (ax1, ax2) = plt.subplots(1, 2)
        plot_matrix(U_target, ax=ax1)
        ax1.set_title('Target')
        plot_matrix(U_total, ax=ax2)
        ax2.set_title('Actual (fid = %.04f)' % fids[0])
        f.savefig(path.join(outdir, 'unitary.%s' % OUTPUT_FMT))
        plt.close(f)

class plot_states(Reporter):
    def run(self, outdir, setups, props, fids, **kwargs):
        f, (ax1, ax2, ax3) = plt.subplots(1, 3)
        plot_matrix(setups[0].inits.T, ax=ax1)
        ax1.set_title('Initial')
        plot_matrix(setups[0].finals.T, ax=ax2)
        ax2.set_title('Final')
        plot_matrix(props[0], ax=ax3)
        ax3.set_title('Actual (fid = %.04f)' % fids[0])
        f.savefig(path.join(outdir, 'states.%s' % OUTPUT_FMT))
        plt.close(f)

class plot_trajectories(Reporter):
    """
    Plot probability trajectories for a given setup.
    """
    def __init__(self, setup, spacing, taylor_order=20):
        super(plot_trajectories, self).__init__(spacing)
        self.setup = setup
        self.taylor_order = taylor_order

    def run(self, outdir, sim_controls, aux_params, dt, n_ss):
        print('Plotting trajectories...')

        dt = dt / float(n_ss)
        setup = self.setup
        t_order = self.taylor_order

        f, axes = plt.subplots(len(self.setup.inits), 1)
        for i_state, (init, final, ax) in enumerate(zip(self.setup.inits, self.setup.finals, axes)):
            probs = []
            psi = init.copy()
            for i, time_slice in enumerate(sim_controls.T):
                L = -1j * dt * (setup.H0 + sum(c*Hc for c,Hc in zip(time_slice, setup.Hcs)))
                psi_k = psi
                for k in range(1, t_order+1):
                    psi_k = L.dot(psi_k) / k
                    psi += psi_k
                probs.append(np.abs(psi)**2)
            ovlp = np.abs(np.sum(final.conj() * psi))**2
            ax.imshow(np.array(probs).T, interpolation='nearest', aspect='auto', origin='lower')
            ax.set_xlim(-0.5, len(probs))
            ax.set_ylim(-0.5, len(psi))
            ax.set_title('State %d, ovlp: %.04f' % (i_state, ovlp))

        f.tight_layout()
        f.savefig(path.join(outdir, 'trajectories.%s' % OUTPUT_FMT))
        plt.close(f)

class plot_cwigs(Reporter):
    def __init__(self, dim, spacing=5, indices=None, max_alpha=3.5, n_pts=100):
        super(plot_cwigs, self).__init__(spacing)
        xs = np.linspace(-3.5, 3.5, 100)
        X, Y = np.meshgrid(xs, xs)
        disps = (X + 1j*Y).flatten()
        self.dim = dim
        self.n_pts = n_pts
        self.M = wigner_mat(disps, dim)
        self.paulis = [
            qutip.qeye(2), qutip.sigmax(), qutip.sigmay(), qutip.sigmaz()
        ]
        self.paulis = [qutip.tensor(p, qutip.qeye(dim)).full() for p in self.paulis]
        self.indices = indices
        if indices is None:
            self.indices = slice(None, None)
        self.fig = None
        self.grid = None


    def run(self, setups, props, aux_params, outdir):
        print('plotting wigners...')
        finals = setups[0].finals[self.indices]
        prop_inits = props[0].T[self.indices]
        if setups[0].gauge_ops is not None:
            gauge_prop = expm(-1j*sum(gv*gop for gv, gop in zip(aux_params, setups[0].gauge_ops)))
            finals = finals.dot(gauge_prop.conj())
            # finals = gauge_prop.dot(finals.T).T
            prop_inits = gauge_prop.conj().T.dot(prop_inits.T).T
        if self.fig is None:
            self.fig = plt.figure()
            self.grid = ImageGrid(self.fig, 111, nrows_ncols=(2*len(finals), 4), axes_pad=0)
            for ax in self.grid:
                ax.set_xticks([])
                ax.set_yticks([])
            for ax, name in zip(self.grid, 'I,X,Y,Z'.split(',')):
                ax.set_title(name)
        fig, grid = self.fig, self.grid
        i = 0
        for k, (prop_init, final) in enumerate(zip(prop_inits, finals)):
            grid[i].set_ylabel('Prop*Init[%d]' % k, rotation='horizontal', ha='right')
            for wig in self.cond_wigs(prop_init):
                grid[i].imshow(wig, vmin=-1, vmax=1)
                i += 1
            grid[i].set_ylabel('Final[%d]' % k, rotation='horizontal', ha='right')
            for wig in self.cond_wigs(final):
                grid[i].imshow(wig, vmin=-1, vmax=1)
                i += 1
        fig.savefig(path.join(outdir, 'cwigs.%s' % OUTPUT_FMT))

    def cond_wigs(self, psi):
        d = psi.shape[0] / 2
        rho = np.outer(psi, psi.conj())
        for op in self.paulis:
            op_rho = op.dot(rho)
            ptrace_op_rho = op_rho[:d,:d] + op_rho[d:,d:]
            yield self.M.dot(vectorize(ptrace_op_rho)).reshape((self.n_pts, self.n_pts))

class verify_from_setup(Reporter):
    """
    Evaluate the fidelity from the given setup. This can serve as a consistency
    check, for instance to ensure the fidelity is unchanged by introducing the
    F state
    """
    def __init__(self, setup, spacing):
        super(verify_from_setup, self).__init__(spacing)
        self.setup = setup

    def run(self, sim_controls, aux_params, dt, n_ss):
        dt = dt / float(n_ss)
        print()
        print('*' * 20+' verifying...', end=' ')
        _, fid, _, _ = self.setup.get_fids(sim_controls, aux_params, dt)
        print('fid = %.7g' % fid)


class verify_with_response(Reporter):
    def __init__(self, setup, spacing, response):
        super(verify_with_response, self).__init__(spacing)
        self.setup = setup
        self.response = response

    def run(self, awg_controls, aux_params, dt, n_ss):
        dt = dt / float(n_ss)
        f = plt.figure()
        controls = np.kron(awg_controls, np.identity(n_ss)[:,0])
        plt.plot(controls[0,:], 'ks')
        controls = np.array([
            np.convolve(controls[i,:], self.response, mode='full')
                for i in range(controls.shape[0])])
        plt.plot(controls[0,:])
        plt.plot(controls[1,:])
        plt.savefig('new_waves.%s' % OUTPUT_FMT)
        print('Verifying with alternate response function...', end=' ')
        _, fid, _, _ = self.setup.get_fids(controls, aux_params, dt)
        print('fid = %.7g' % fid)
        plt.close(f)


class verify_master_equation(Reporter):
    def __init__(self, setup, c_ops, spacing):
        super(verify_master_equation, self).__init__(spacing)
        self.setup = setup
        self.c_ops = c_ops

    def run(self, sim_controls, dt, n_ss):
        print('='*80)
        print('verifying with qutip...')
        dt = dt / float(n_ss)
        H0_arr, Hcs_arr = self.setup.H0, self.setup.Hcs
        inits, finals = self.setup.inits, self.setup.finals
        dims = [H0_arr.shape[0]]
        H0 = qutip.Qobj(H0_arr, dims=[dims, dims])
        Hcs = [qutip.Qobj(Hc, dims=[dims, dims]) for Hc in Hcs_arr]
        c_ops = [qutip.Qobj(op, dims=[dims, dims]) for op in self.c_ops]
        inits = [qutip.Qobj(s, dims=[dims, [1]]) for s in inits]
        finals = [qutip.Qobj(s, dims=[dims, [1]]) for s in finals]
        n_states = len(inits)

        H = [H0] + [[Hc, w] for Hc, w in zip(Hcs, sim_controls)]
        tlist = dt * np.arange(sim_controls.shape[1])
        fid = 0

        for i in range(n_states):
            for j in range(i, n_states):
                init = inits[i] * inits[j].dag()
                final = finals[i] * finals[j].dag()
                prop_init = qutip.mesolve(H, init, tlist, c_ops, {}).states[-1]
                sub_fid = (final * prop_init.dag()).tr()
                print('sub_fid', i, j, sub_fid)
                if i != j:
                    sub_fid *= 2
                fid += sub_fid.real

        fid = np.sqrt(fid) / n_states
        print('tot fid', fid)
        print('='*80)


class verify_sensitivity(Reporter):
    """
    Evaluate the fidelity from the given setup varying some parameters.
    delta_list is a tuple/list containing a tuple of (name, H, amps), e.g.
        [('sz', Hsigmaz, np.linspace(-1e-4, 1e-4, 5))]
    """
    def __init__(self, setup, spacing, delta_list):
        super(verify_sensitivity, self).__init__(spacing)
        self.setup = setup
        self.delta_list = delta_list

    def run(self, sim_controls, aux_params, dt, n_ss, outdir):
        dt = dt / float(n_ss)
        _, fid0, _, _ = self.setup.get_fids(sim_controls, aux_params, dt)

        for name, dH, amps in self.delta_list:
            if isinstance(dH, qutip.Qobj):
                dH = dH.full()
            print('Varying', name)
            fids = []
            orig_H0 = self.setup.H0.copy()
            for amp in amps:
                if amp == 0:
                    fid = fid0
                else:
                    self.setup.H0 = orig_H0 + amp * dH
                    _, fid, _, _ = self.setup.get_fids(sim_controls, aux_params, dt)
                print('\t%.4g: %.4g' % (amp, fid))
                fids.append(fid)
            self.setup.H0 = orig_H0

            f, ax = plt.subplots(1, 1)
            ax.plot(np.array(amps) / 2 / np.pi * 1e6, 1 - np.array(fids), 'ks')
            ax.set_xlabel('Amplitude / 2pi [kHz]')
            ax.set_ylabel('Infidelity')
            ax.set_title('Sensitivity to ' + name)
            f.savefig(path.join(outdir, 'sens_%s.%s' % (name, OUTPUT_FMT)))
            plt.close(f)


class verify_dispersion_sensitivity(Reporter):
    """
    Evaluate the fidelity from the given setup varying dispersion.
    disp_list specifies the dispersions to use, in fractional change / GHz.
    """
    def __init__(self, setup, spacing, disp_list):
        super(verify_dispersion_sensitivity, self).__init__(spacing)
        self.setup = setup
        self.disp_list = disp_list

    def run(self, sim_controls, aux_params, dt, n_ss, outdir):
        dt = dt / float(n_ss)

        n_ctrls = sim_controls.shape[0]
        controlsF = [np.fft.rfft(sim_controls[i,:]) for i in range(n_ctrls)]
        freqs = np.fft.rfftfreq(sim_controls.shape[1], dt)

        print('Varying dispersion')
        fids = []
        for amp in self.disp_list:
            filt = (1 + freqs * amp)
            filt[filt<0] = 0
            filt[filt>2] = 2
            controls = np.array([
                np.fft.irfft(controlsF[i] * filt)
                    for i in range(n_ctrls)])
            _, fid, _, _ = self.setup.get_fids(controls, aux_params, dt)
            print('\t%.4g: %.4g' % (amp, fid))
            fids.append(fid)

        f, ax = plt.subplots(1, 1)
        ax.plot(np.array(self.disp_list) * 10, 1 - np.array(fids), 'ks')
        ax.set_xlabel('pct change @ 100 MHz')
        ax.set_ylabel('Infidelity')
        ax.set_title('Dispersion sensitivity')
        f.savefig(path.join(outdir, 'sens_dispersion.%s' % OUTPUT_FMT))
        plt.close(f)


def plot_matrix(M, ax=None, smap=None, labels=None):
    yshape, xshape = M.shape
    if max(xshape, yshape) < 8:
        lw = 1
    else:
        lw = 0.5
    R = 0.4
    if ax is None:
        f = plt.figure()
        ax = f.add_subplot(111)
    ax.set_aspect('equal')
    ax.set_xlim(0, xshape)
    ax.set_ylim(0, yshape)
    for x in range(xshape):
        ax.plot([x, x], [0, yshape], 'k', lw=lw)
    for y in range(yshape):
        ax.plot([0, xshape], [y, y], 'k', lw=lw)

    for i in range(yshape):
        for j in range(xshape):
            vec = M[i,j]
            if np.abs(vec)**2 < 1e-3:
                continue
            if smap:
                fc = smap.to_rgba(np.abs(vec)**2)
            else:
                fc = 'None'
            x = j
            y = yshape - i - 1
            ax.add_patch(mpatches.Circle([x+0.5,y+0.5], R*np.abs(vec), fc=fc, lw=lw))
            ax.plot([x+0.5, x+0.5+R*vec.real], [y+0.5,y+0.5+R*vec.imag], 'k', lw=lw)

    if labels is None:
        ax.set_xticks([])
        ax.set_yticks([])
    else:
        ax.set_xticks(np.arange(xshape)+0.5)
        ax.set_yticks(np.arange(yshape)+0.5)
        labels = ['$|%s\\rangle$' % s for s in labels]
        ax.set_xticklabels(labels)
        ax.set_yticklabels(list(reversed(labels)))

    return ax

def cond_wigs(state, xs):
    mat = state.data.todense().reshape(state.dims[0])
    mat = mat[:2, :]
    q_vecs_t, coefs, c_vecs = svd(mat, full_matrices=False)
    q_vecs = q_vecs_t.T
    assert len(q_vecs) == len(c_vecs) == 2, (c_vecs.shape, q_vecs.shape)
    c_vecs = np.diag(coefs).dot(c_vecs)
    q_vecs = list(map(qutip.Qobj, q_vecs))
    c_vecs = list(map(qutip.Qobj, c_vecs))
    # assert q.tensor(q_vecs[0], c_vecs[0]) + q.tensor(q_vecs[1], c_vecs[1]) == state
    paulis = [qutip.qeye(2), qutip.sigmax(), qutip.sigmay(), qutip.sigmaz()]
    wigs = []
    for q_op in paulis:
        wig = 0
        for j in range(2):
            wig += (q_vecs[j].dag() * q_op * q_vecs[j])[0,0] * qutip.wigner(c_vecs[j] * c_vecs[j].dag(), xs, xs, g=2)
        od_coef = (q_vecs[0].dag() * q_op * q_vecs[1])[0,0]
        od_wig = wig_imag(c_vecs[0] * c_vecs[1].dag(), xs, xs, g=2)
        wig += od_coef * od_wig
        wig += od_coef.conj() * od_wig.conj()
        wigs.append(wig.real)
    return wigs

def wig_imag(rho, xvec, yvec, g=2):
    """
    Using Laguerre polynomials from scipy to evaluate the Wigner function for
    the density matrices :math:`|m><n|`, :math:`W_{mn}`. The total Wigner
    function is calculated as :math:`W = \sum_{mn} \\rho_{mn} W_{mn}`.
    """

    M = np.prod(rho.shape[0])
    X, Y = np.meshgrid(xvec, yvec)
    A = 0.5 * g * (X + 1.0j * Y)
    W = np.zeros(np.shape(A), dtype=np.complex)

    B = 4 * abs(A) ** 2
    for m in range(M):
        if abs(rho[m, m]) > 0.0:
            W += np.real(rho[m, m] * (-1) ** m * genlaguerre(m, 0)(B))
        for n in range(m + 1, M):
            if abs(rho[m, n]) > 0.0:
                W += 2.0 * rho[m, n] * (-1)**m * (2*A)**(n-m) * sqrt(factorial(m)/factorial(n)) * genlaguerre(m, n-m)(B)
    return 0.5 * W * g ** 2 * np.exp(-B / 2) / pi


def optimize_gauge(props, targets, gauge_ops):
    '''
    Optimize a set of gauge transformation given by gauge_ops.
    The parameters are lists with one element for each setup.
    '''

    n_gauge = len(gauge_ops[0])

    def gauge_transform(g_vals, g_ops):
        total = None
        if n_gauge == 1:
            g_vals = [g_vals]
        for g_val, g_op in zip(g_vals, g_ops):
            g_prop = expm(-1j * g_val * g_op)
            if total is None:
                total = g_prop
            else:
                total = total.dot(g_prop)
        return total

    def apply_gauges(gauge_vals, g_ops_row, targ):
        t = gauge_transform(gauge_vals, g_ops_row)
        return np.dot(targ, t)

    def gauge_cost(gauge_vals):
        cost = 0
        for prop, targ, g_ops_row in zip(props, targets, gauge_ops):
            norm = np.sum(abs(targ)**2)
            targ_after = apply_gauges(gauge_vals, g_ops_row, targ)
            if targ_after.shape == prop.shape:
                overlap = np.sum(targ_after.conj() * prop) / norm
            else:
                overlap = np.sum(targ_after.T.conj() * prop) / norm
            fid = abs(overlap)
            cost += 1 - fid
        cost = cost / len(props)
        return cost

    ranges = [slice(0, 2*np.pi, .2)] * n_gauge
    g_vals = brute(gauge_cost, ranges)

    return g_vals, [apply_gauges(g_vals, g_ops, targ) for g_ops, targ in zip(gauge_ops, targets)]

def wigner_mat(disps, d):
    """
    Construct the matrix M such that M(alpha)*vec(rho) = Wigner(alpha)
    The matrix M will be of dimension (N, d^2) where N is the number of
    displacements and d is the maximum photon number.

    Here vec(rho) deconstructs rho into a basis of d^2 hermitian operators.
    The first d elements of vec(rho) are the diagonal elements of rho, the
    next d*(d-1)/2 elements are the real parts of the upper triangle,
    and the last d*(d-1)/2 elements are the imaginary parts of the upper triangle.

    Elements of M are then M(a, (i, j)) = <j|D(-a) P D(a) |i> with displacement
    operator D and parity operator P.

    See http://dx.doi.org/10.1103/PhysRev.177.1882, esp. eq. 7.15
    """
    n_disp = len(disps)
    n_offd = (d * (d - 1)) // 2
    dm = np.zeros((n_disp, d * d))
    A = disps
    B = 4 * abs(A) ** 2
    i = 0
    for m in range(d):
        dm[:, m] = np.real((-1) ** m * genlaguerre(m, 0)(B))
        for n in range(m + 1, d):
            off_d = 2.0*(-1)**m * (2*A)**(n-m) * sqrt(factorial(m)/float(factorial(n))) * genlaguerre(m, n-m)(B)
            dm[:, d + i] = off_d.real
            dm[:, d + n_offd + i] = -off_d.imag
            i += 1
    dm = np.einsum('ij,i->ij', dm, np.exp(-B / 2))
    return dm

def vectorize(rho):
    d = rho.shape[0]
    n_offd = d*(d-1)//2
    ret = np.zeros(d**2)
    i = 0
    for m in range(d):
        ret[m] = rho[m, m].real
        for n in range(m+1, d):
            ret[d+i] = rho[m, n].real
            ret[d+n_offd+i] = rho[m, n].imag
            i += 1
    return ret
