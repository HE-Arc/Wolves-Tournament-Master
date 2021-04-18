
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from qutip import *
import qutip.control.pulseoptim as pulseoptim

def jaynesCummingsHamiltonian(
    cavityDimension, omegaCavity, omegaQubit, g, 
    anharmonicityCavity=0, anharmonicityQubit=0,
    chi2ndOrder=0, regime = 'dispersive',
):
    """
    regimes = ['full','rotating wave','dispersive']
    ket2dm(fock(2,1)) == destroy(2).dag()*destroy(2)
    """
    a  = tensor(destroy(cavityDimension), qeye(2))
    sm = tensor(qeye(cavityDimension), destroy(2))
    Hcavity = omegaCavity*a.dag()*a + \
        anharmonicityCavity/2 * (a.dag())**2 * a**2
    Hqubit = omegaQubit*sm.dag()*sm + \
        anharmonicityQubit/2 * (sm.dag())**2 * sm**2
    positionCavity = a  + a.dag()
    positionQubit  = sm + sm.dag()
    numberCavity = a.dag()*a
    numberQubit  = sm.dag()*sm
    Icavity = qeye(cavityDimension)
    #Iqubit = qeye(2)
    if regime == 'full': 
        Hinteraction = g * positionCavity * positionQubit
    elif regime == 'rotating wave':
        Hinteraction = g * (a*sm.dag() + a.dag()*sm)
    elif regime == 'dispersive':
        assert omegaCavity != omegaQubit,\
            "omegaCavity != omegaQubit when regime == 'dispersive'"
        chi = g**2 / abs(omegaCavity-omegaQubit)
        Hinteraction = chi * numberCavity * numberQubit
    Hinteraction2 = chi2ndOrder/2*sm.dag()*sm*(a.dag())**2 * a**2
    H = Hcavity + Hqubit + Hinteraction + Hinteraction2
    controlsDict = {
        'sigmax': tensor(Icavity,sigmax()),
        'sigmay': tensor(Icavity,sigmay()),
        'a': a, 'a_dagger': a.dag(),
        'sigma-': sm, 'sigma+': sm.dag(), 
    }
    observables = [
        {'Hcavity':Hcavity, 'Hqubit':Hqubit},
        {'numberCavity':numberCavity, 'numberQubit':numberQubit},
        {'positionCavity':positionCavity, 'positionQubit':positionQubit},
    ]
    operators = { 
        'a': a, 'a_dagger': a.dag(),
        'sigma-': sm, 'sigma+': sm.dag(), 
    }
    return H, controlsDict, observables, operators

