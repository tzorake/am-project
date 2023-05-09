import os
import numpy as np


class OscType:
    CHAOS       = -5 # хаос
    FAKE        = -4 # затухающии колебания
    UNDEF       = -3 # undef
    SP_IND_FREQ = -2 # суперпозиция независимых частот
    IND_FREQ    = -1 # 2 независимые частоты
    HARMONIC    =  0 # гармоники


class HeuristicSpectrumAnalyzer:
    DIF_LONG = 2
    ANAL_EPS = 0.01

    def __init__(self):
        pass


    def set_data(self, time, values, start_time = -1, end_time = -1):
        assert(len(time) == len(values))

        def closest_power_of_two(n):
            n = int(np.log2(n))
            return 2 ** n

        start_time = time[0] if start_time == -1 else start_time
        end_time = time[-1] if end_time == -1 else end_time

        start_time = next(t for t in time if t >= start_time)
        end_time = next(t for t in reversed(time) if t <= end_time)

        start_index = np.where(time == start_time)[0][0]
        end_index = np.where(time == end_time)[0][0]

        if start_index >= end_index:
            raise Exception("start_time cannot be greater than end_time.")

        time = time[start_index:end_index]
        values = values[start_index:end_index]

        time_len = len(time)
        n = closest_power_of_two(time_len)

        self.time = time[:n]
        self.values = values[:n]
    

    def get_interval_type(self, norm: list, n: int, d_omega: float) -> int:
        idx_eps: int = int(HeuristicSpectrumAnalyzer.ANAL_EPS / d_omega)
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

                if (bif_pos < n):
                    current_type = simple_nums[i]
                else: 
                    current_type = OscType.HARMONIC
                break
        
        if(current_type == 0):
            for i in range(0, n):
                if(norm[i] != 0):
                    break
            if(i != n):
                if(peak_test(n - i - 1)):
                    current_type = OscType.SP_IND_FREQ
                else:
                    div: float =  float(n) / i
                    if (np.abs(div - int(div) - 0.5) < 0.5 - HeuristicSpectrumAnalyzer.ANAL_EPS):
                        current_type = OscType.IND_FREQ
                    else:
                        current_type = OscType.UNDEF
        else:
            next_type: int = self.get_interval_type(norm, bif_pos, d_omega)

            if (next_type < 0):
                current_type = next_type
            
            if (current_type >= 2 and current_type < next_type):
                current_type = next_type
        
        return current_type


    def get_type(self, data: list, n: int, d_omega: float) -> int:
        main_freq: int = 0
        peak_number: int = 0

        data[0] = data[1] # special hack for constant part of signal - freq 0

        max: float = data[0]
        min: float = data[0]

        for i in range(1, n):
            if (data[i] < min):
                min = data[i]
            if (data[i] > max):
                max = data[i]
        
        if (max <= -7):
            return OscType.FAKE

        max -= min

        if (max == 0):
            max = 1

        norm = [0] * n

        for i in range(3, n - 1):
            if ((data[i] > data[i - 1]) and (data[i] > data[i + 1])):
                if((data[i] - data[i - HeuristicSpectrumAnalyzer.DIF_LONG]) / HeuristicSpectrumAnalyzer.DIF_LONG / d_omega >= 1.0):
                    norm[i] = (data[i] - min) / max

        peak_number = 0

        for i in range(0, n // 4):
            if (norm[i] != 0):
                peak_number += 1

        if (peak_number > n // 40 + 1):
            return OscType.CHAOS; 

        for i in range(0, n):
            if (norm[i] > 0.99):
                break
        
        main_freq = i
        self.mf = main_freq * d_omega

        return self.get_interval_type(norm, main_freq, d_omega)


    def evaluate(self, max_omega: float, time_step: float):
        n = len(self.values)

        for i in range(0, n):
            if np.isnan(self.values[i]):
                return OscType.UNDEF
        
        self.do_fft()

        n = len(self.values)
        d_omega = (2 * np.pi) / (n * time_step)
        spec_size = np.minimum(int(max_omega / d_omega), n // 2)

        return self.get_type(self.result, spec_size, d_omega)


    def do_fft(self) -> int:
        n = len(self.values)
        fft = np.fft.fft(self.values, n)
        half = len(fft) // 2
        fft = fft[1:]

        self.result = np.log(np.abs(fft[:half]))