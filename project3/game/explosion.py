import random
import time

class Explosion:
    def __init__(self, pos):
        self.particles = [[list(pos), [random.uniform(-1,1)*0.1 for _ in range(3)]] for _ in range(20)]
        self.start_time = time.time()
        self.duration = 1.0

    def update(self):
        for p in self.particles:
            for i in range(3):
                p[0][i] += p[1][i]

    def is_done(self):
        return (time.time() - self.start_time) > self.duration
