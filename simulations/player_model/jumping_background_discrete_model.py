
import numpy as np
import utils
import scipy.stats
from scipy.misc import logsumexp

import sys
sys.path.append("../utils/")
import stats

import copy

import config

class JumpingBackgroundDiscrete():

    def __init__(self, sizes = [484,280], noise = 0.2, width = config.DISCRETE_BG_RADIUS, jump_freq = config.SPOT_SHIFT_PROB):

        self.sizes = sizes
        self.noise = noise
        self.width = width
        self.jump_freq = jump_freq
        
        self.pos_limits = config.POS_LIMITS
        self.shape = 'rectangle'

    def prior_sample(self, n = 1):
        return np.column_stack([np.random.choice(self.sizes[0],n), np.random.choice(self.sizes[1],n)])
    
    # prove mixed exact/sampled particle filter is valid by showing a
    # sample from p(x)p(y|x) = p(y|x) sum_z p(x | z) p(z) can be
    # achieved by enumerating z, then sampling an x within each z and
    # weighting based on the likelihood
    def transition(self, samples):
        x = []
        for i in range(len(samples)):
            if np.random.random() < self.jump_freq:
                x += [self.prior_sample(n = 1)[0]]
            else:
                x += [copy.deepcopy(samples[i])]
        
        return x
            
    def likelihood(self, loc, obs, x):
        
        collision = utils.check_collision(loc, self.pos_limits, self.shape, update = False)
        if not collision:
            try:
                assert abs(obs - 0.1) < 1e-12 or abs(obs - 1.0) < 1e-12
            except:
                import pdb; pdb.set_trace()
            expected = self.score( self.dists(loc, x) )
        else:
            try:
                assert obs < 1e-12
            except:
                import pdb; pdb.set_trace()

            expected = np.array([0.0]*len(x))
        
        return -(obs - expected)**2/float(2*self.noise**2)
        
    def score(self, dist):
        return 0.1 + 0.9 * (dist < self.width)
    
    def dists(self, loc, x):
        return np.sqrt(np.sum((np.array(loc) - x)**2, 1))

    def get_beliefs(self, samples):
        beliefs = np.zeros(self.sizes)
        for s in samples:
            x = min(max(0,round(s[0])),self.sizes[0]-1)
            y = min(max(0,round(s[1])),self.sizes[1]-1)
            beliefs[x,y] += 1
        beliefs = beliefs / np.sum(beliefs)
        return beliefs
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
