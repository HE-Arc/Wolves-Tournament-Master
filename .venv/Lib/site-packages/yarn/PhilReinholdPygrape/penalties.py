import numpy as np


def make_lin_amp_cost(reg, iq_pairs=False):
    def calc_amp_cost(waves):
        if iq_pairs:
            i_waves = waves[0::2]
            q_waves = waves[1::2]
            amp_costs = reg * (i_waves**2 + q_waves**2)
            d_cost_i = 2 * reg * i_waves
            d_cost_q = 2 * reg * q_waves
            d_cost = np.zeros_like(waves)
            d_cost[0::2] = d_cost_i
            d_cost[1::2] = d_cost_q
        else:
            amp_costs = reg * waves**2
            d_cost = 2 * reg * waves
        cost = amp_costs.sum()
        return cost, d_cost
    return calc_amp_cost


def make_amp_cost(reg, thresh, offset=0, iq_pairs=False, widcs=None):
    def calc_amp_cost(waves):
        if widcs != None:
            waves[widcs,:] = 0

        waves = waves - offset
        if iq_pairs:
            i_waves = waves[0::2]
            q_waves = waves[1::2]
            amp_costs = np.exp((i_waves**2 + q_waves**2) / (2*thresh**2))
            d_cost_i = (i_waves / thresh**2) * amp_costs
            d_cost_q = (q_waves / thresh**2) * amp_costs
            d_cost = np.zeros_like(waves)
            d_cost[0::2] = d_cost_i
            d_cost[1::2] = d_cost_q
            amp_costs -= 1
        else:
            amp_costs = np.exp(waves**2 / (2*thresh**2))
            d_cost = ((waves / thresh**2) * amp_costs)
            amp_costs -= 1
        cost = amp_costs.sum()
        return reg*cost, reg*d_cost
    return calc_amp_cost


def make_lin_deriv_cost(reg, iq_pairs=False):
    def calc_deriv_cost(waves):
        waves_back = np.roll(waves, -1, axis=1)
        diff = waves - waves_back
        f_diff = reg * diff**2
        df_diff = 2 * reg * diff
        cost = f_diff.sum()
        d_cost = df_diff - np.roll(df_diff, +1, axis=1)
        return cost, d_cost
    def calc_iq_deriv_cost(waves):
        i_waves = waves[0::2]
        q_waves = waves[1::2]
        a_waves = i_waves**2 + q_waves**2
        cost, dca = calc_deriv_cost(a_waves)
        dci = 2 * dca * i_waves
        dcq = 2 * dca * q_waves
        d_cost = np.zeros_like(waves)
        d_cost[0::2] = dci
        d_cost[1::2] = dcq
        return cost, d_cost
    if iq_pairs:
        return calc_iq_deriv_cost
    else:
        return calc_deriv_cost


def make_deriv_cost(reg, thresh, widcs=None):
    def calc_deriv_cost(waves):
        if widcs != None:
            waves[widcs,:] = 0

        waves_back = np.roll(waves, -1, axis=1)
        diff = waves - waves_back
        f_diff = reg * np.exp(diff**2/(2*thresh**2))
        df_diff = (diff / thresh**2) * f_diff
        cost = f_diff.sum() - reg*waves.size
        d_cost = df_diff - np.roll(df_diff, +1, axis=1)
        return cost, d_cost
    return calc_deriv_cost

def make_direct_penalty(reg, alpha, bmask):

    def direct_penalty(waves):
        dc = np.zeros_like(waves)
        
        v1 = 1 + np.exp(alpha*waves[bmask])
        v2 = 1 + np.exp(-alpha*waves[bmask])
        c2 = (reg / alpha) * np.sum(np.log(v1) + np.log(v2))
        dc[bmask] = reg * (1/v2 - 1/v1)

        return c2, dc
        
    return direct_penalty
        
def make_l1_penalty(reg, alpha):
    def l1_penalty(waves):
        a_waves = abs(waves)
        mask = a_waves > (25. / alpha)

        c1 = reg * np.sum(a_waves[mask])
        dc = np.zeros_like(waves)
        dc[mask] = reg * np.sign(waves[mask])
        
        v1 = 1 + np.exp(alpha*waves[~mask])
        v2 = 1 + np.exp(-alpha*waves[~mask])
        c2 = (reg / alpha) * np.sum(np.log(v1) + np.log(v2))
        dc[~mask] = reg * (1/v2 - 1/v1)
        
        return c1 + c2, dc
    return l1_penalty


def make_l1_wvd_penalty_cuda(reg, plen, blocksize=16, use_double=False):
    from pygrape.cuda_l1_wvd import l1_wvd
    runner = l1_wvd(plen, blocksize=blocksize, use_double=use_double)
    def penalty(waves):
        cost = 0
        d_cost = np.zeros_like(waves)
        for i, (zi, zq) in enumerate(zip(waves[0::2], waves[1::2])):
            c, dci, dcq = runner(zi, zq)
            cost += c
            d_cost[2*i, :] = dci
            d_cost[2*i + 1, :] = dcq
        return reg * cost, reg * d_cost
    return penalty


def make_tail_cost(reg, response, impulse_data=None):
    def penalty(controls):
        tail_len = response.shape[1]
        n_ctrls, plen = controls.shape
        if impulse_data is not None:
            controls = np.kron(controls, impulse_data)
        c_controls = controls[::2] + 1j*controls[1::2]
        conv_controls = np.array([
            np.convolve(c_controls[i,:], response[i], mode='full')
            for i in range(n_ctrls/2)
        ])
        cost = reg * np.sum(abs(conv_controls[:,-tail_len:])**2)
        mask = np.zeros_like(conv_controls)
        mask[:,-tail_len:] = 1
        d_cost_d_conv_controls = 2 * reg * mask * conv_controls
        d_cost_d_c_controls = np.array([
            np.convolve(d_cost_d_conv_controls[i,:], response[i, ::-1].conj(), mode='valid')
            for i in range(n_ctrls/2)
        ])
        d_cost = np.array([d_cost_d_c_controls.real, d_cost_d_c_controls.imag])
        d_cost = d_cost.transpose(1,0,2).reshape((n_ctrls, -1))
        if impulse_data is not None:
            d_cost = (impulse_data * d_cost.reshape((n_ctrls, plen, len(impulse_data)))).sum(axis=2)
        return cost, d_cost
    return penalty


if __name__ == '__main__':
    n_ctrls, plen = 5, 10
    waves = np.random.randn(n_ctrls, plen)
    amp_cost = make_amp_cost(1e-3, 30)
    c1, g = amp_cost(waves)
    errs = []
    for i in range(n_ctrls):
        for j in range(plen):
            d_waves = np.zeros_like(waves)
            d_waves[i, j] = 1e-7
            c2, _ = amp_cost(waves + d_waves)
            g1 = g[i, j]
            g2 = (c2 - c1) / 1e-7
            errs.append(abs(g2 - g1) / min(abs(g1), abs(g2)))
    print('Max Err:', max(errs))
