import random
from functools import wraps
from bisect import bisect

uniform = True
n = 4
length = 4348
log_delay = 5
process_iterations = 800

def process(func):
    @wraps(func)
    def wrapper(queue, *args, **kwargs):
        process_total = process_index = 0
        while True:
            process_total += func(*args, **kwargs)
            process_index += 1

            if process_index % process_iterations == 0:
                queue.put(process_total)
                process_total = 0
    
    return wrapper

@process
def simulate_nonuniform(size, ngram_cum_weights):
    unique = set()
    for i in range(length // n):
        unique.add(bisect(ngram_cum_weights, random.random()))

        if len(unique) == size:
            return size
    else:
        return len(unique)

@process
def simulate_uniform(size):
    unique = set()
    for i in range(length // n):
        unique.add(random._inst._randbelow(size))
    return len(unique)

if __name__ == '__main__':
    from itertools import accumulate
    from ngrams import Ngrams
    import multiprocessing as mp
    import time
    import math

    ngrams = Ngrams()
    if uniform:
        exact_probability = ngrams.ugrams_uniform(n, length)
        target = simulate_uniform
        args = (26 ** n,)

    else:
        exact_probability = ngrams.ugrams(n, length)
        ngram_cum_weights = [float(value) for value in accumulate(ngrams.en_ngrams[n - 1].freqs.values())]
        ngram_cum_weights[-1] = 1.0
        target = simulate_nonuniform
        args = (len(ngram_cum_weights), ngram_cum_weights)

    queue = mp.Queue()
    for i in range(mp.cpu_count() - 1):
        mp.Process(target=target, args=(queue, *args)).start()

    start_time = time.time()
    total = index = 0
    while True:
        time.sleep(log_delay)
        results = []
        while not queue.empty():
            results.append(queue.get())
        
        total += sum(results)
        index += len(results) * process_iterations
        if index:
            print(f'Exact: {round(exact_probability, 6)}, Simulated: {total / index:.6f} (1e{math.log10(index):.6f} iterations, {round(time.time() - start_time):04} seconds)')