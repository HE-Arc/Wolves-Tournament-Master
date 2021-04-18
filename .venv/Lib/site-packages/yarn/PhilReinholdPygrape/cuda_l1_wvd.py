import pycuda.autoinit
import pycuda.driver as drv
import numpy as np
from pycuda.compiler import SourceModule
import time

src = """
#if %(use_double)d
#define FLOAT double
#define IFLOAT unsigned long long int
#define F2I __double_as_longlong
#define I2F __longlong_as_double
#else
#define FLOAT float
#define IFLOAT unsigned int
#define F2I __float_as_int
#define I2F __int_as_float
#endif

// Problem size
#define N %(N)d
// Block size
#define Nb %(Nb)d
// Flattened block size
#define Nb2 %(Nb2)d
// Block data size
#define Nbd %(Nbd)d
// Number of memory writes per thread
#define Nwrite %(Nwrite)d

__device__ FLOAT atomicAddF(FLOAT* address, FLOAT val)
{
    IFLOAT* address_as_ull = (IFLOAT*)address;
    IFLOAT old = *address_as_ull, assumed;
    do {
        assumed = old;
        old = atomicCAS(
            address_as_ull, assumed,
            F2I(val + I2F(assumed))
        );
    } while (assumed != old);
    return I2F(old);
}

__device__ __constant__ FLOAT wsr[N];
__device__ __constant__ FLOAT wsi[N];

__global__ void kernel(FLOAT *global_out_data, FLOAT *global_in_data) {
    const int nb = threadIdx.x;            // X position in block
    const int n = nb + Nb*blockIdx.x;      // X position in full grid
    const int k = blockIdx.y;
    const int j = nb;
    const int m_max = min(n+1, N-n);
    int m, p;
    FLOAT Wnkr, Wnki;
    FLOAT dWnpmkr, dWnpmki;
    FLOAT dWnmmkr, dWnmmki;
    FLOAT Wnk_angle_r, Wnk_angle_i;
    FLOAT wkmr, wkmi;
    FLOAT znpmr, znpmi, zcnmmr, zcnmmi;
    FLOAT Knmr, Knmi;
    FLOAT cnk, bd;

    __shared__ FLOAT block_out_data[Nbd];
    FLOAT *block_cost = block_out_data;
    FLOAT *block_grad_r = block_out_data + 1;
    FLOAT *block_grad_i = block_out_data + (N+1);

    FLOAT *zr = global_in_data;
    FLOAT *zi = global_in_data + N;

    for (m=0; m<Nwrite; m++) {
        p = j + m*Nb2;
        if (p < Nbd)
            block_out_data[p] = 0;
    }
    __syncthreads();

    if (n < N && k < N) {
        Wnkr = 0;
        Wnki = 0;
        for (m=0; m<m_max; m++) {
            wkmr = wsr[k*m %% N];
            wkmi = wsi[k*m %% N];
            znpmr = zr[n+m];
            znpmi = zi[n+m];
            zcnmmr = zr[n-m];
            zcnmmi = -zi[n-m];
            Knmr = znpmr*zcnmmr - znpmi*zcnmmi;
            Knmi = znpmi*zcnmmr + znpmr*zcnmmi;
            Wnkr += wkmr*Knmr - wkmi*Knmi;
            Wnki += wkmi*Knmr + wkmr*Knmi;
        }

        cnk = sqrt(Wnkr*Wnkr + Wnki*Wnki);
        atomicAddF(block_cost, cnk);

        if (cnk > 1e-7) {
            Wnk_angle_r = Wnkr / cnk;
            Wnk_angle_i = -Wnki / cnk;
            for (m=0; m<m_max; m++) {
                wkmr = wsr[k*m %% N];
                wkmi = wsi[k*m %% N];
                znpmr = zr[n+m];
                znpmi = zi[n+m];
                zcnmmr = zr[n-m];
                zcnmmi = -zi[n-m];
                dWnpmkr = wkmr*zcnmmr - wkmi*zcnmmi;
                dWnpmki = wkmr*zcnmmi + wkmi*zcnmmr;
                dWnmmkr = wkmr*znpmr - wkmi*znpmi;
                dWnmmki = wkmr*znpmi + wkmi*znpmr;
                atomicAddF(block_grad_r + (n+m), Wnk_angle_r*dWnpmkr - Wnk_angle_i*dWnpmki);
                atomicAddF(block_grad_i + (n+m), -(Wnk_angle_r*dWnpmki + Wnk_angle_i*dWnpmkr));
                atomicAddF(block_grad_r + (n-m), Wnk_angle_r*dWnmmkr - Wnk_angle_i*dWnmmki);
                atomicAddF(block_grad_i + (n-m), Wnk_angle_r*dWnmmki + Wnk_angle_i*dWnmmkr);
            }
        }
    }

    __syncthreads();

    for (m=0; m<Nwrite; m++) {
        p = j + m*Nb2;
        if (p < Nbd) {
            bd = block_out_data[p];
            if (bd != 0)
                atomicAddF(global_out_data + p, bd);
        }
    }

}
"""

def l1_wvd(N, block_size=16, use_double=False):
    Nb = block_size
    Ng = int(np.ceil(float(N) / Nb))
    Nb2 = Nb
    Nbd = 2*N + 1
    Nwrite = int(np.ceil(float(Nbd) / Nb2))
    cfg = dict(N=N, Ng=Ng, Nb=Nb, Nb2=Nb2, Nbd=Nbd, Nwrite=Nwrite, use_double=use_double)
    mod = SourceModule(src % cfg)
    kernel = mod.get_function('kernel')
    dtype = np.float64 if use_double else np.float32
    w0 = np.exp(-2j * np.pi / N)
    ws = np.array([w0**k for k in range(N)])
    wsr_cmem = mod.get_global('wsr')[0]
    wsi_cmem = mod.get_global('wsi')[0]
    drv.memcpy_htod(wsr_cmem, np.ascontiguousarray(ws.real.astype(dtype)))
    drv.memcpy_htod(wsi_cmem, np.ascontiguousarray(ws.imag.astype(dtype)))

    def run(z, zi=None):
        if zi is None:
            indata = np.concatenate([z.real, z.imag])
        else:
            indata = np.concatenate([z, zi])
        indata = drv.In(np.ascontiguousarray(indata.astype(dtype)))
        outdata = drv.InOut(np.zeros(Nbd, dtype=dtype))
        kernel(outdata, indata, block=(Nb, 1, 1), grid=(Ng, N))
        cost = outdata.array[0]
        grad_r = outdata.array[1:N+1]
        grad_i = outdata.array[N+1:]
        return cost, grad_r, grad_i

    return run

if __name__ == '__main__':
    import sys
    N = int(sys.argv[2])
    Nb = int(sys.argv[1])
    i = int(sys.argv[3])
    eps = float(sys.argv[4])
    runner = l1_wvd(N, Nb)
    np.random.seed(5432)
    z = np.random.randn(N) + 1j*np.random.randn(N)
    print('warming up?', end=' ')
    for _ in range(3):
        c, dcr, dci = runner(z)
        print('.', end=' ')
    print('result =', c)
    print('calling...', end=' ')
    t0 = time.time()
    c1, dcr, dci = runner(z)
    t1 = time.time() - t0
    print('finished:', t1)
    dz = np.eye(N)[i]
    c2, _, _ = runner(z + eps*dz)
    c3, _, _ = runner(z + 1j*eps*dz)
    dcr2 = (c2 - c1) / eps
    dci2 = (c3 - c1) / eps
    print('grad re: calc =', dcr[i], 'appx =', dcr2)
    print('grad im: calc =', dci[i], 'appx =', dci2)
    drv.stop_profiler()
