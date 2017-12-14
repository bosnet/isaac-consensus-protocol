import threading
import time
import logging
import random

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)

class Counter(object):
    def __init__(self, start = 0):
        self.lock = threading.Lock()
        self.value = start
    def increment(self):
        logging.debug('Waiting for a lock')
        self.lock.acquire()
        try:
            logging.debug('Acquired a lock')
            self.value = self.value + 1
        finally:
            logging.debug('Released a lock')
            self.lock.release()

def worker(c):
    for i in range(2):
        r = random.random()
        logging.debug('Sleeping %0.02f', r)
        time.sleep(r)
        c.increment()
    logging.debug('Done')

if __name__ == '__main__':
    counter = Counter()
    for i in range(2):
        t = threading.Thread(target=worker, args=(counter,))
        t.start()

    logging.debug('Waiting for worker threads')
    main_thread = threading.currentThread()
    for t in threading.enumerate():
        if t is not main_thread:
            t.join()
    logging.debug('Counter: %d', counter.value)
