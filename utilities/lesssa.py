import numpy as np
from utilities.lesss import LESpecSanoSawada


class LESSSA:
    def __init__(self, e_dim, tau, iterations, eps_min, eps_step, min_neighbors):
        self.lesss = LESpecSanoSawada(e_dim, tau, iterations, eps_min, eps_step, min_neighbors)

    def set_data(self, time, values, start_time = -1, end_time = -1):
        start_time = time[0] if start_time == -1 else start_time
        end_time = time[-1] if end_time == -1 else end_time

        start_time = next(t for t in time if t >= start_time)
        end_time = next(t for t in reversed(time) if t <= end_time)

        start_index = np.where(time == start_time)[0][0]
        end_index = np.where(time == end_time)[0][0]

        if start_index >= end_index:
            raise Exception("start_time cannot be greater than end_time.")

        self.data = values[start_index:end_index]

    def evaluate(self):
        if (self.data is None):
            raise Exception("self.data is used before initialization")

        if (len(self.data) == 0):
            raise Exception("self.data has zero length")

        self.lesss.calculate(self.data)

        result = self.lesss.result
        filtered = list(filter(lambda x: x < 0, result))

        return len(filtered), result


if __name__ == '__main__':
    stms = [
        [ 0.1,  0.1,  0.1,  0.1],
        [ 0.1,  0.1,  0.1, -0.1],
        [ 0.1,  0.1, -0.1,  0.1],
        [ 0.1,  0.1, -0.1, -0.1],
        [ 0.1, -0.1,  0.1,  0.1],
        [ 0.1, -0.1,  0.1, -0.1],
        [ 0.1, -0.1, -0.1,  0.1],
        [ 0.1, -0.1, -0.1, -0.1],
        [-0.1,  0.1,  0.1,  0.1],
        [-0.1,  0.1,  0.1, -0.1],
        [-0.1,  0.1, -0.1,  0.1],
        [-0.1,  0.1, -0.1, -0.1],
        [-0.1, -0.1,  0.1,  0.1],
        [-0.1, -0.1,  0.1, -0.1],
        [-0.1, -0.1, -0.1,  0.1],
        [-0.1, -0.1, -0.1, -0.1]
    ]

    lesssa = LESSSA()
    
    for data in stms:
        lesssa.set_data(data)
        result = lesssa.evaluate()
        print(f'Result: {result}')