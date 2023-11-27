from __future__ import print_function
import logging
from tulip import transys, spec, synth

logging.basicConfig(level=logging.WARNING)
logging.getLogger('tulip.spec.lexyacc').setLevel(logging.WARNING)
logging.getLogger('tulip.synth').setLevel(logging.WARNING)
logging.getLogger('tulip.interfaces.omega').setLevel(logging.WARNING)

N = 3  # Size of the grid
sys = transys.FTS()

# Define the states of the system
states = ['X{}{}{}'.format(i, j, k) for i in range(N) for j in range(N) for k in range(N)]
sys.states.add_from(states)
sys.states.initial.add('X000')  # start in state X000

# Define the allowable transitions
for i in range(N):
    for j in range(N):
        for k in range(N):
            current_state = 'X{}{}{}'.format(i, j, k)
            next_states = set()

            if i > 0:
                next_states.add('X{}{}{}'.format(i - 1, j, k))  # Move up
            if i < N - 1:
                next_states.add('X{}{}{}'.format(i + 1, j, k))  # Move down
            if j > 0:
                next_states.add('X{}{}{}'.format(i, j - 1, k))  # Move left
            if j < N - 1:
                next_states.add('X{}{}{}'.format(i, j + 1, k))  # Move right
            if k > 0:
                next_states.add('X{}{}{}'.format(i, j, k - 1))  # Move in the third dimension
            if k < N - 1:
                next_states.add('X{}{}{}'.format(i, j, k + 1))  # Move in the third dimension

            sys.transitions.add_comb({current_state}, next_states)

# Add atomic propositions to the states
sys.atomic_propositions.add_from({'home', 'lot'})
sys.states.add('X000', ap={'home'})
sys.states.add('X{}{}{}'.format(N-1, N-1, N-1), ap={'lot'})

# Environment variables and specification
env_vars = {'park'}
env_init = set()  # empty set
env_prog = '!park'
env_safe = set()  # empty set

# System specification
sys_vars = {'X0reach'}  # infer the rest from TS
sys_init = {'X0reach'}
sys_prog = {'home'}  # []<>home
sys_safe = {'(X (X0reach) <-> lot) || (X0reach && !park)'}
sys_prog |= {'X0reach'}

# Create the specification
specs = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                    env_safe, sys_safe, env_prog, sys_prog)

# Controller synthesis
specs.moore = True
specs.qinit = r'\E \A'
ctrl = synth.synthesize(specs, sys=sys)
assert ctrl is not None, 'unrealizable'

print(ctrl)