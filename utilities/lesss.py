from time import time
import numpy as np


class BoxAssistedFnn:
    def __init__(self, box_size, time_series_size):
        self.box_size = box_size
        self.i_box_size = box_size - 1
        self.boxes = np.zeros((box_size, box_size), dtype=np.int32)
        self.list = np.zeros(time_series_size, dtype=np.int32)
        self.found = np.zeros(time_series_size, dtype=np.int32)


    def put_in_boxes(self, series, epsilon, start_index, end_index, x_shift, y_shift):
        self.boxes.fill(-1)
        
        for i in range(start_index, end_index):
            x = int(series[i + x_shift] / epsilon) & self.i_box_size
            y = int(series[i + y_shift] / epsilon) & self.i_box_size
            self.list[i] = self.boxes[x][y]
            self.boxes[x][y] = i


    def find_neighbors_j(self, series, e_dim, tau, epsilon, act):
        nf = 0
        dx = 0.0

        x = int(series[act] / epsilon) & self.i_box_size
        y = x

        for i in range(x - 1, x + 2):
            i1 = i & self.i_box_size

            for j in range(y - 1, y + 2):
                element = self.boxes[i1][j & self.i_box_size]

                while (element != -1):
                    for k in range(0, e_dim):
                        k1 = -k * tau

                        dx = np.abs(series[k1 + act] - series[element + k1])

                        if (dx > epsilon):
                            break

                    if (dx <= epsilon):
                        self.found[nf] = element
                        nf += 1

                    element = self.list[element]

        return nf


class LESpecSanoSawada:
    output_interval = 10000
    eps_max = 1.0

    def __init__(self, e_dim, tau, iterations, eps_min, eps_step, min_neighbors):
        self.e_dim = e_dim
        self.tau = tau
        self.iterations = iterations
        self.eps_set = eps_min != 0
        self.eps_min = eps_min
        self.eps_step = eps_step
        self.min_neighbors = min_neighbors
        
        self.result = np.zeros(e_dim, dtype=np.float64)

        self.error_avg = 0.0
        self.neighbors_avg = 0.0
        self.eps_avg = 0.0
        self.vector = None
        self.matrix = None
        self.abstand = None
        self.indexes = None
        self.count = 0


    def calculate(self, time_series):
        series = time_series[:]
        
        if (self.iterations == 0):
            self.iterations = len(series)

        if (self.min_neighbors > (len(series) - self.tau * (self.e_dim - 1) - 1)):
            raise Exception("self.min_neighbors > (len(series) - self.tau * (self.e_dim - 1) - 1)")
        
        fnn = BoxAssistedFnn(512, len(series))

        self.error_avg = 0.0

        series_min = np.min(series)
        series_max = np.max(series)
        series = (series - series_min) / (series_max - series_min)

        interval = series_max - series_min
        variance = np.var(series)

        if (variance == 0.0):
            raise Exception("variance == 0.0")
    
        self.eps_min = self.eps_min / interval if self.eps_set else interval * 1000

        dynamics = np.zeros(self.e_dim, dtype=np.float64)
        factor = np.zeros(self.e_dim, dtype=np.float64)
        lfactor = np.zeros(self.e_dim, dtype=np.float64)
        delta = np.zeros((self.e_dim, self.e_dim), dtype=np.float64)
        self.vector = np.zeros(self.e_dim + 1, dtype=np.float64)
        self.matrix = np.zeros((self.e_dim + 1, self.e_dim + 1), dtype=np.float64)
        self.count = 0

        self.indexes = self.make_index(self.e_dim, self.tau)

        delta = np.random.rand(*delta.shape)

        lfactor = self.gram_schmidt(delta)
        start = min(self.iterations, len(series) - self.tau)
        self.abstand = np.zeros(len(series), dtype=np.float64)
        start_time = int(time() * 1000)

        for i in range((self.e_dim - 1) * self.tau, start):
            self.count += 1
            self.make_dynamics(series, fnn, dynamics, i)
            self.make_iteration(dynamics, delta)
            lfactor = self.gram_schmidt(delta)

            for j in range(0, self.e_dim):
                factor[j] += np.log(lfactor[j]) / self.tau

            elapsed = int(time() * 1000) - start_time

            if (elapsed > self.output_interval or (i == (start - 1))):
                start_time = int(time() * 1000)

                for j in range(0, self.e_dim):
                    self.result[j] = factor[j] / self.count


    def sort(self, series, fnn, act, n_found):
        imax = n_found
        this = 0
        enough = False
        n_found_initial = n_found

        for i in range(0, imax):
            hf = fnn.found[i]

            if (hf != act):
                maxdx = np.abs(series[act] - series[hf])

                for j in range(1, self.e_dim):
                    delta = self.indexes[j]
                    dx = np.abs(series[act - delta] - series[hf - delta])
                    if (dx > maxdx): 
                        maxdx = dx

                self.abstand[i] = maxdx
            else:
                this = i
    
        if (this != (imax - 1)):
            self.abstand[this] = self.abstand[imax - 1]
            fnn.found[this] = fnn.found[imax - 1]

        for i in range(0, self.min_neighbors):
            for j in range(i + 1, imax - 1):
                if (self.abstand[j] < self.abstand[i]):
                    dswap = self.abstand[i]
                    self.abstand[i] = self.abstand[j]
                    self.abstand[j] = dswap
                    iswap = fnn.found[i]
                    fnn.found[i] = fnn.found[j]
                    fnn.found[j] = iswap

        if ((not self.eps_set) or (self.abstand[self.min_neighbors - 1] >= self.eps_min)):
            n_found = self.min_neighbors
            enough = True
            maxeps = self.abstand[self.min_neighbors - 1]

            return maxeps, n_found, enough

        for i in range(self.min_neighbors, imax - 2):
            for j in range(i + 1, imax - 1):
                if (self.abstand[j] < self.abstand[i]):
                    dswap = self.abstand[i]
                    self.abstand[i] = self.abstand[j]
                    self.abstand[j] = dswap
                    iswap = fnn.found[i]
                    fnn.found[i] = fnn.found[j]
                    fnn.found[j] = iswap
            
            if (self.abstand[i] > self.eps_min):
                n_found = i + 1
                enough = True
                maxeps = self.abstand[i]

                return maxeps, n_found, enough

        maxeps = self.abstand[imax - 2]
        n_found = n_found_initial
        return maxeps, n_found, enough


    def solve_le(self, mat, vec):
        n = len(mat)
        for i in range(n - 1):
            maxi = i + np.argmax(np.abs(mat[i:, i]))
            if maxi != i:
                mat[[i, maxi]] = mat[[maxi, i]]
                vec[[i, maxi]] = vec[[maxi, i]]
            pivot = mat[i, i]
            if pivot == 0:
                raise ValueError("Singular matrix.")
            for j in range(i + 1, n):
                q = -mat[j, i] / pivot
                mat[j, i:] += q * mat[i, i:]
                vec[j] += q * vec[i]
        vec[-1] /= mat[-1, -1]
        for i in range(n - 2, -1, -1):
            vec[i] -= np.dot(mat[i, i + 1:], vec[i + 1:])
            vec[i] /= mat[i, i]
        return vec


    def invert_matrix(self, mat):
        size = mat.shape[0]
        imat = np.zeros((size, size))

        for i in range(size):
            vec = np.zeros(size)
            vec[i] = 1

            hmat = mat.copy()

            self.solve_le(hmat, vec)

            for j in range(size):
                imat[j, i] = vec[j]

        return imat


    def make_dynamics(self, series, fnn, dynamics, act):
        i, hi, j, hj, k, t = act, 0, 0, 0, 0, act
        n_found = 0
        found_eps = 0.0
        epsilon = self.eps_min / self.eps_step
        while True:
            epsilon *= self.eps_step
            if epsilon > self.eps_max:
                epsilon = self.eps_max
            fnn.put_in_boxes(series, epsilon, (self.e_dim - 1) * self.tau, len(series) - self.tau, 0, 0)
            n_found = fnn.find_neighbors_j(series, self.e_dim, self.tau, epsilon, act)
            if n_found > self.min_neighbors:
                got_enough = False
                found_eps, n_found, got_enough = self.sort(series, fnn, act, n_found)
                if got_enough:
                    break
            if epsilon >= self.eps_max:
                break

        self.neighbors_avg += n_found
        self.eps_avg += found_eps

        if not self.eps_set:
            self.eps_min = self.eps_avg / self.count

        if n_found < self.min_neighbors:
            raise ValueError("Not enough neighbors found.")

        vector = np.zeros(self.e_dim + 1)
        matrix = np.zeros((self.e_dim + 1, self.e_dim + 1))

        for i in range(n_found):
            act = fnn.found[i]
            matrix[0, 0] += 1.0
            for j in range(self.e_dim):
                matrix[0, j + 1] += series[act - self.indexes[j]]
            for j in range(self.e_dim):
                hv1 = series[act - self.indexes[j]]
                hj = j + 1
                for k in range(j, self.e_dim):
                    matrix[hj, k + 1] += series[act - self.indexes[k]] * hv1

        for i in range(self.e_dim + 1):
            for j in range(i, self.e_dim + 1):
                matrix[i, j] /= np.float64(n_found)
                matrix[j, i] = matrix[i, j]

        imat = self.invert_matrix(matrix)
        vector = np.zeros(self.e_dim + 1)

        for i in range(n_found):
            act = fnn.found[i]
            hv = series[act + self.tau]
            vector[0] += hv
            for j in range(self.e_dim):
                vector[j + 1] += hv * series[act - self.indexes[j]]

        for i in range(self.e_dim + 1):
            vector[i] /= np.float64(n_found)

        new_vec = 0.0

        for i in range(self.e_dim + 1):
            new_vec += imat[0, i] * vector[i]

        for i in range(1, self.e_dim + 1):
            hi = i - 1
            dynamics[hi] = 0.0
            for j in range(self.e_dim + 1):
                dynamics[hi] += imat[i, j] * vector[j]

        for i in range(self.e_dim):
            new_vec += dynamics[i] * series[t - self.indexes[i]]

        tmp = new_vec - series[t + self.tau]
        self.error_avg += tmp * tmp


    def gram_schmidt(self, delta):
        e_dim = delta.shape[0]
        dnew = np.zeros((e_dim, e_dim))
        stretch = np.zeros(e_dim)

        for i in range(e_dim):
            diff = np.zeros(e_dim)

            for j in range(i):
                norm = delta[i] @ dnew[j]
                diff -= norm * dnew[j]

            norm = np.linalg.norm(delta[i] + diff)
            stretch[i] = norm

            dnew[i] = (delta[i] + diff) / norm

        delta[:] = dnew[:]

        return stretch


    def make_iteration(self, dynamics, delta):
        dnew = np.zeros((self.e_dim, self.e_dim), dtype=np.float64)
        
        for i in range(0, self.e_dim):
            dnew[i][0] = dynamics[0] * delta[i][0]

            for k in range(1, self.e_dim):
                dnew[i][0] += dynamics[k] * delta[i][k]

            for j in range(1, self.e_dim):
                dnew[i][j] = delta[i][j - 1]
        
        for i in range(0, self.e_dim):
            for j in range(0, self.e_dim):
                delta[i][j] = dnew[i][j]


    def make_index(self, e_dim, delay):
        return np.arange(0, e_dim * delay, delay, dtype=np.int32)


if __name__ == '__main__':
    
    file_name = 'txt/01b3ec1f-c6f1-4253-873d-1a3c90251cbb.txt'
    data = np.loadtxt(file_name)
    t, w = data[:, 0], data[:, 1]

    lesss = LESpecSanoSawada(2, 1, 0, 0, 1.2, 30)
    series = w[:1000]
    done = lesss.calculate(series)

    print(f'e_dim: {lesss.e_dim}, tau: {lesss.tau}, iterations: {lesss.iterations}, eps_min: {lesss.eps_min}, eps_step: {lesss.eps_step}, min_neighbors: {lesss.min_neighbors}')
    print(f'Result code: {done}')
    print(f'Result: {lesss.result}')

