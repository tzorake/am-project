import matplotlib.pyplot as plt
import numpy as np

def closest_power_of_two(n):
    n = int(np.log2(n))
    return 2**n

def main():
    x = np.linspace(0, 100, 1280)
    n_fft = closest_power_of_two(len(x))
    x = x[:n_fft]
    y = 0.6*np.sin(2*np.pi*50*x) + 3*np.random.randn(len(x))+ np.sin(2*np.pi*120*x)
    
    dt = x[1] - x[0] 
    fft = np.fft.fft(y, n_fft)
    half = len(fft)//2
    fft = fft[1:]

    stm = np.log(abs(fft[:half]))
    nyquist = 1.0 / (2 * dt)
    freq = 2.0*np.pi*nyquist*(np.linspace(1, half, half)) / half

    fig, (ax1, ax2) = plt.subplots(nrows=2)

    ax1.plot(x, y)
    ax2.plot(freq, stm)

    plt.tight_layout()
    plt.show()
    


if __name__ == '__main__':
    np.random.seed(3)
    main()