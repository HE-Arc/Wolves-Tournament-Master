
import matplotlib.pyplot as plt

def plot(result, ctrlNames=None):
    ctrlNames = ctrlNames or [str(i) for i in range(len(result.controls))]
    for i,ctrl in enumerate(result.controls):
        plt.step(result.ts, ctrl, label=ctrlNames[i])
    plt.legend(); plt.show()