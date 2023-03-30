import os
import numpy as np
from time import gmtime, strftime


CHUNK_SIZE = 16382
DIF_LONG = 2
ANAL_EPS = 0.01

real = np.double


'''

typedef enum {
  UNDEF = -3,
  CHAOS = -5,
  FAKE = -4,
  HARMONIC = 0,
  IND_FREQ = -1,
  SP_IND_FREQ = -2
} osc_type;

'''
class osc_type:
    CHAOS = -5
    FAKE = -4
    UNDEF = -3
    SP_IND_FREQ = -2
    IND_FREQ = -1
    HARMONIC = 0

    @staticmethod
    def types() -> dict:
        return {
            osc_type.CHAOS       : 'CHAOS',
            osc_type.FAKE        : 'FAKE',
            osc_type.UNDEF       : 'UNDEF',
            osc_type.SP_IND_FREQ : 'SP_IND_FREQ',
            osc_type.IND_FREQ    : 'IND_FREQ',
            osc_type.HARMONIC    : 'HARMONIC',
        }

    @staticmethod
    def colors() -> dict:
        return {
            osc_type.CHAOS       : '#0000ff',
            osc_type.FAKE        : '#00ff00',
            osc_type.UNDEF       : '#ff0000',
            osc_type.SP_IND_FREQ : '#ff00ff',
            osc_type.IND_FREQ    : '#ffff00',
            osc_type.HARMONIC    : '#0f0f0f',
        }

    @staticmethod
    def as_str(t):
        types = osc_type.types()
        return types.get(t, None)


class HeuristicSpectrumAnalyzer:
    def __init__(self):
        self.mf: real

        self.hsa_n: int = 0
        self.hsa_array: list = []
        
        self.log = 'log.txt'


    '''

    void hsa_read_data (double time, double value, double hsa_start_time)
    {
    if (time == 0)
        hsa_n = 0;
    if (time >= hsa_start_time)
        {
        if (hsa_n >= hsa_curent_size)
        {
        hsa_curent_size += CHUNK_SIZE;
        hsa_array =
            (c_type*) realloc (hsa_array, hsa_curent_size * sizeof (c_type));
        }
        hsa_array[hsa_n++] = value;
        }
    }

    '''
    def hsa_read_data(self, time: real, value: real, hsa_start_time: real):
        if (time == 0):
            self.hsa_n = 0

        if (time >= hsa_start_time):
            if (self.hsa_n >= len(self.hsa_array)):
                self.hsa_array = self.hsa_array + [0] * CHUNK_SIZE
            
            self.hsa_array[self.hsa_n] = value
            self.hsa_n += 1


    '''

    static osc_type get_interval_type(real *norm, int n, double domega) 
    {
        double anal_eps = ANAL_EPS;
        int idx_eps = (int) (anal_eps / domega);
        int simple_nums[] = {2, 3, 5, 7, 11, 13, 17, 23, 29, 31, 37, 39}; //simple numbers table
        int bif_pos = 0;
        int i = sizeof(simple_nums) / sizeof(simple_nums[0]) - 1;
        int current_type = 0; 

        int peak_test(int i)
        {
            int eps = (i < idx_eps) ? i : idx_eps;
            for(; eps >= 0; eps--)
            {
                if(norm[i + eps] != 0)
                return i + eps;
                if(norm[i - eps] != 0)
                return i - eps;
            }
            return 0;
        }
        for(i = 0; i < sizeof(simple_nums) / sizeof(simple_nums[0]); i++)
        {
            int peaks = 0;
            int j;
            for(j = 1; j < simple_nums[i]; j++) 
            {
                int idx = j * n / simple_nums[i];
                if(peak_test(idx))
                peaks++;
                else 
                break;
            }

            if(peaks != 0) 
            {
                bif_pos = peak_test(n / simple_nums[i]);
                if(bif_pos < n) 
                current_type = simple_nums[i];
                else
                current_type = HARMONIC;
                break;
            }
        }
        if(current_type == 0)
        {
            for(i = 0; i < n; i++)
            if(norm[i] != 0)
                break;
            if(i != n)
            if(peak_test(n - i - 1)) 
                current_type = SP_IND_FREQ;
            else
            {
            double div = (double)n / i;
            if(fabs(div - (int)div - 0.5) < 0.5 - anal_eps) 
                {
                current_type = IND_FREQ;
                }
            else
                current_type = UNDEF;

            }
        }
        else 
        {
            osc_type next_type = get_interval_type(norm, bif_pos, domega);
            if (next_type < 0) 
            current_type = next_type;
            if ((current_type >= 2) && (current_type < next_type))
            current_type = next_type;
        }
        return current_type;
        
    }

    '''
    def get_interval_type(self, norm: list, n: int, domega: real) -> int:
        anal_eps: real = ANAL_EPS
        idx_eps: int =  int(anal_eps / domega)
        simple_nums: list = [2, 3, 5, 7, 11, 13, 17, 23, 29, 31, 37, 39] # simple numbers table
        bif_pos: int = 0
        i: int = len(simple_nums) - 1
        current_type: int = 0

        def peak_test(i: int) -> int:
            for eps in range(i if (i < idx_eps) else idx_eps, -1, -1):
                if(norm[i + eps] != 0):
                    return i + eps
                if(norm[i - eps] != 0):
                    return i - eps
            return 0
        
        for i in range(0, len(simple_nums)):
            peaks: int = 0
            for j in range(1, simple_nums[i]):
                idx: int = j * n // simple_nums[i]
                if(peak_test(idx)):
                    peaks += 1
                else:
                    break

            if(peaks != 0):
                bif_pos = peak_test(n // simple_nums[i])
                if(bif_pos < n):
                    current_type = simple_nums[i]
                else:
                    current_type = osc_type.HARMONIC
                break
        
        if(current_type == 0):
            for i in range(0, n):
                if(norm[i] != 0):
                    break
            if(i != n):
                if(peak_test(n - i - 1)):
                    current_type = osc_type.SP_IND_FREQ
                else:
                    div: real =  real(n) / i
                    if (np.abs(div - int(div) - 0.5) < 0.5 - anal_eps):
                        current_type = osc_type.IND_FREQ
                    else:
                        current_type = osc_type.UNDEF
        else:
            next_type: int = self.get_interval_type(norm, bif_pos, domega)

            if (next_type < 0) :
                current_type = next_type
            
            if (current_type >= 2 and current_type < next_type):
                current_type = next_type
        
        return current_type

    '''

    static osc_type get_type (c_type * data, int n, double * mf, double domega)
    {
    int i;
    int main_freq;
    double max, min;
    int peak_number, bifurcations;
    real * norm;
    int div;


    data[0] = data[1]; /* special hack for constant part of signal - freq 0 */

    max = min = data[0];
    for (i = 1; i < n; ++i)
        {
        if (data[i] < min)
            min = data[i];
        if (data[i] > max)
            max = data[i];
        }
        
    if (max <= -7)
        return FAKE;

    max -= min;
    if (max == 0)
        max = 1;

    /* will be automatically freed */
    norm = (real*) alloca (sizeof (real) * n);
    memset (norm, 0, sizeof (real) * n);
    for (i = 3; i < n - 1; ++i)
        if ((data[i] > data[i - 1]) && (data[i] > data[i + 1]) )
        if((data[i] - data[i - DIF_LONG]) / DIF_LONG / domega >= 1.0)
            norm[i] = (data[i] - min) / max;

    peak_number = 0;
    for (i = 0; (i < n / 4); ++i)
        if (norm[i] != 0)    
        ++peak_number;

    if (peak_number > n / 40 + 1)
        return CHAOS; 

    for (i = 0; i < n; ++i)
        if (norm[i] > 0.99)
        break;
    
    main_freq = i;
    *mf = main_freq * domega;

    return get_interval_type(norm, main_freq, domega);

    }

    '''
    def get_type(self, data: list, n: int, domega: real) -> int:
        main_freq: int = 0
        peak_number: int = 0

        data[0] = data[1] # special hack for constant part of signal - freq 0

        max: real = data[0]
        min: real = data[0]

        for i in range(1, n):
            if (data[i] < min):
                min = data[i]
            if (data[i] > max):
                max = data[i]
        
        if (max <= -7):
            return osc_type.FAKE

        max -= min

        if (max == 0):
            max = 1

        norm = [0] * n

        for i in range(3, n - 1):
            if ((data[i] > data[i - 1]) and (data[i] > data[i + 1])):
                if((data[i] - data[i - DIF_LONG]) / DIF_LONG / domega >= 1.0):
                    norm[i] = (data[i] - min) / max

        peak_number = 0

        for i in range(0, n // 4):
            if (norm[i] != 0):
                peak_number += 1

        if (peak_number > n // 40 + 1):
            return osc_type.CHAOS; 

        for i in range(0, n):
            if (norm[i] > 0.99):
                break
        
        main_freq = i
        self.mf = main_freq * domega

        return self.get_interval_type(norm, main_freq, domega)


    '''

    static int do_fft (double * in, int n)
    {
    int i;

    if (n & (n - 1))
        fprintf (logfd, "Warning hsa_n is not radix 2\n");
    
    while (n & (n - 1))
        n &= n - 1;

    if (n <= 1)
        {
        ERROR_ ("Critical error : do_fft failed (n = %d)\n", n);
        return 0;
        }

    gsl_fft_real_radix2_transform (in, 1, n);

    in[0] = log (sqrt (in[0] * in[0]) / n);  /* DC component */
    for (i = 1; i < n / 2; ++i)  /* (i < N/2 rounded up) */
        in[i] = log (sqrt (in[i] * in[i] + in[n - i] * in[n - i]) / n);
    in[n / 2] = log (sqrt (in[n / 2] * in[n / 2]) / n); /* Nyquist freq. */
    return n;
    }

    '''
    def do_fft(self, signal: list, n: int) -> int:
        # if (n & (n - 1)):
        #     self.write(f'Warning : hsa_n is not radix 2\n')
        
        # while (n & (n - 1)):
        #     n &= n - 1

        # if (n <= 1):
        #     self.write(f'Critical error : do_fft failed (n = {n})\n')
        #     return 0

        # self.hsa_array = np.log(np.abs(np.fft.fft(signal, n)))

        # return n

        def closest_power_of_two(n):
            n = int(np.log2(n))
            return 2**n

        n = closest_power_of_two(len(signal))
        
        fft = np.fft.fft(signal, n)
        half = len(fft)//2
        fft = fft[1:]

        self.hsa_array = np.log(abs(fft[:half]))

        return n

    '''

    static int hsa_save_spectrum (char * filename, c_type * spectrum, int n, double domega)
    {
    FILE * fd = NULL;
    int i;
    
    if (!filename)
        return FALSE;
    if (!(fd = fopen (filename, "w")))
        return FALSE;
    for (i = 0; i < n; ++i)
        fprintf (fd, "%g %g\n", i * domega, spectrum[i]);
    fclose (fd);
    return TRUE;
    }

    '''
    def hsa_save_spectrum(self, filename: str, spectrum: list, n: int, domega: real):
        if (not filename):
            return False

        omega = np.array([i * domega for i in range(0, n)])
        to_save = list(zip(omega, spectrum[:n]))

        np.savetxt(f'{filename}.stm', to_save)
    
        return True
        
    '''

    osc_type hsa_main (double * mf, char * filename, double max_omega, double time_step)
    {
    int i;
    int spec_size;
    double domega;
    
    for (i = 0; i < hsa_n; ++i)
        if (gsl_isnan (hsa_array[i]))
        return UNDEF;
    
    if (!(hsa_n = do_fft (hsa_array, hsa_n)))
        return UNDEF;

    domega = (2 * M_PI) / (hsa_n * time_step);
    spec_size = MIN (max_omega / domega, hsa_n / 2);
    
    if (filename)
        if (!hsa_save_spectrum (filename, hsa_array, spec_size, domega))
        fprintf (logfd, "Failed to save spectrum to file %s\n", filename);
    fflush (logfd);
    
    return get_type (hsa_array, spec_size, mf, domega);
    }

    '''
    def hsa_main(self, filename: str, max_omega: real, time_step: real):
        spec_size: int = 0
        domega: real = 0.0
        
        for i in range(0, self.hsa_n):
            if np.isnan(self.hsa_array[i]):
                return osc_type.UNDEF
        
        self.hsa_n = self.do_fft(self.hsa_array, self.hsa_n)

        if (not self.hsa_n):
            return osc_type.UNDEF

        domega = (2 * np.pi) / (self.hsa_n * time_step)
        spec_size = np.minimum(int(max_omega / domega), self.hsa_n // 2)
        
        if (filename):
            if (not self.hsa_save_spectrum(filename, self.hsa_array, spec_size, domega)):
                self.write(f'Failed to save spectrum to file {filename}\n' )
        
        return self.get_type(self.hsa_array, spec_size, domega)
    
    def write(self, message):
        with open(self.log, 'a') as f:
            time = strftime('%d %b %Y %H:%M:%S', gmtime())
            f.write(f'{time} {message}')


if __name__ == '__main__':

    hsa = HeuristicSpectrumAnalyzer()

    for file in os.scandir('txt'):
        data = np.loadtxt(file.path)
        t, w = data[:, 0], data[:, 1]

        for t, w in zip(t, w):
            hsa.hsa_read_data(t, w, 1000.0)
        
        omega0 = 20.3
        time_step = 0.015625

        o_type: int = hsa.hsa_main(file.name, omega0 * 2.1, time_step)
        print(osc_type.as_str(o_type))