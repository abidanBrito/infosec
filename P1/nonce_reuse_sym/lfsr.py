import operator
import random
from functools import reduce

class LFSR(object):

    def __init__(self, size, initial_state, taps):
        assert size == len(initial_state) == len(taps), "unequal sizes for taps and state"
        for x in initial_state:
            assert x in (0,1), "state consists of an array of bits"
        for x in taps:
            assert x in (0,1), "taps consists of an array of bits"
        self.taps = taps
        self.state = initial_state
    
    def _clock(self):
        temp = [a & b for a,b in zip(self.state, self.taps)]
        update = reduce(operator.xor, temp)
        output = self.state[0]
        self.state = self.state[1:] + [update]
        return output

    def output(self, length):
        result = []
        for _ in range(length):
            result.append(self._clock())
        return result