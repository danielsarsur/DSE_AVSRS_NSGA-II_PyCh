# Model variables
lv, dv, vmaxv, av = 3.0, 1.5, 0.5, 0.5 # Vehicle: load time, column width, max speed, acceleration
ll, dl, vmaxl, al = 2.0, 2.8, 2.0, 2.0 # Lift: load time, tier height, max speed, acceleration
lc, dc, vc = 1.0, 1.5, 5.0 # Conveyor: load time, aisle width, speed
iat_retrieve, iat_store = 15, 15

# System exploration space
Aisles_min, Aisles_max = 1, 5
Levels_min, Levels_max = 1, 20
Columns_min, Columns_max = 15, 25 # total columns, including buffer size
Buf_Cap_min, Buf_Cap_max = 1, 3
N_SP, N_RP, N_LP, N_VP = 6,6,8,6

# Specifications
Slots_min, Slots_max = 900,1100 # n_aisles * n_levels * (n_columns - buf_cap) * 2

# GA parameters
POP_SIZE = 30
NUM_GENERATIONS = 20
NUM_MUTATIONS = 25
NUM_RECOMB = 15
MAXIMIZATION = False
REPETITIONS = 30
confidence_level = 0.95

# Simulation parameters
std_threshold, min_samples = 0.0001, 50