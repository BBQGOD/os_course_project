import random
from time import perf_counter, sleep
from multiprocessing import Pool
from pygtrie import Trie

D = 768
B = 12
V = 30000
# TYPE = 'sequential'
# TYPE = 'batch'
TYPE = 'prefix_batch'
SAMPLE_NUM = 50

job_times = [0] * SAMPLE_NUM
random.seed(42)

def proc_inputs(input_ids, inf=False, prefix=0, jobid=0):
    '''input_ids: (batch_size, seq_len)'''
    batch_size, seq_len = input_ids
    if inf:
        sleep_time = B * (seq_len**2 + 2*prefix*seq_len) * D + 12 * B * seq_len * D**2 + V * seq_len * D
    else:
        sleep_time = seq_len**2 * D + seq_len * D**2

    sleep_time *= 1e-10
    sleep_time *= 1 + 0.25 * (batch_size - 1)
    print('sleep_time: ', sleep_time)
    sleep(sleep_time)
    if inf:
        job_times[jobid] = perf_counter() - job_times[jobid]


def sequential(pool, seq_len):
    for i in range(0, SAMPLE_NUM):
        input_ids = (1, seq_len)
        prefix = random.randint(seq_len//2, seq_len)
        job_times[i] = perf_counter()
        pool.apply_async(proc_inputs, args=(input_ids, True, prefix, i))
        sleep(0.1)

def batch(pool, batch_size, seq_len):
    flen = 0
    for i in range(1, SAMPLE_NUM+1):
        tlen = random.randint(seq_len//2, seq_len)
        flen = max(tlen, flen)
        if i % batch_size == 0:
            input_ids = (batch_size, seq_len)
            prefix = flen
            job_times[i//batch_size] = perf_counter()
            pool.apply_async(proc_inputs, args=(input_ids, True, prefix, i//batch_size))
            flen = 0
        sleep(0.1)

def prefix_batch(pool, batch_size, seq_len):
    flen = 0
    for i in range(0, SAMPLE_NUM):
        tlen = random.randint(seq_len//8, seq_len*3//8)
        # in real scenario, we can use a trie to store the queries, along with query times
        flen = max(tlen, flen)
        if i % batch_size == 0:
            input_ids = (batch_size, seq_len-flen)
            prefix = flen
            job_times[i//batch_size] = perf_counter()
            pool.apply_async(proc_inputs, args=((1, prefix), False, 0, i//batch_size))
            pool.apply_async(proc_inputs, args=(input_ids, True, 0, i//batch_size))
            flen = 0
        sleep(0.1)

if __name__ == '__main__':
    batch_size = 4
    seq_len = 128

    timer = perf_counter()
    pool = Pool(processes=3)
    if TYPE == 'sequential':
        sequential(pool, seq_len)
    elif TYPE == 'batch':
        batch(pool, batch_size, seq_len)
    elif TYPE == 'prefix_batch':
        prefix_batch(pool, batch_size, seq_len)
    else:
        raise ValueError('Unknown type: {}'.format(TYPE))

    pool.close()
    pool.join()
    total_time = perf_counter() - timer
    print('total_time: ', total_time)
    print('throughput: ', SAMPLE_NUM / total_time)
    if TYPE == 'sequential':
        print('average_time: ', sum(job_times) / SAMPLE_NUM)
    elif TYPE == 'batch':
        print('average_time: ', sum(job_times) / (SAMPLE_NUM // batch_size))
    elif TYPE == 'prefix_batch':
        print('average_time: ', sum(job_times) / (SAMPLE_NUM // batch_size))
    else:
        raise ValueError('Unknown type: {}'.format(TYPE))
