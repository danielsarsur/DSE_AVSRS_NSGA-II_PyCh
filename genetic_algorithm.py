import random
import math
import numpy as np
from AVSRS import *
from config import *
from scipy import stats


alpha = stats.t.ppf((1 + confidence_level) / 2, df=(REPETITIONS - 1))
factor = alpha / math.sqrt(REPETITIONS)

def Creep_Mutation_Dim(v, v_min, v_max, min_percent = 1):
    percent = 1 - (1 - min_percent) * (v - v_min) / (v_max - v_min)
    delta = random.uniform(1 - percent, 1 + percent)
    return int(np.clip(round(v * delta), v_min, v_max))

def Creep_Mutation_Buf(v, v_min, v_max):
    return int(np.clip(v + random.randint(-1, 1), v_min, v_max))

def Random_Resetting(v_min, v_max):
    return random.randint(v_min, v_max)

def Arithmetic_Crossover(v1, v2):
    return round((v1 + v2) / 2)

def Uniform_Crossover(v1, v2):
    return v1 if random.random() < 0.5 else v2

def feasibility_check(c, min_s, max_s):
    return True if min_s <= c[0] * c[1] * (c[2] - c[3]) * 2 <= max_s else False

def Initial_Pop():
    population = []
    max_attempts = 5000
    attempts = 0

    while len(population) < POP_SIZE and attempts < max_attempts:
        
        aisles = random.randint(Aisles_min, Aisles_max)
        levels = random.randint(Levels_min, Levels_max)
        slots = random.randint(Columns_min, Columns_max)
        buf_cap = random.randint(Buf_Cap_min, Buf_Cap_max)
        sp_id = random.randint(0, N_SP-1)
        rp_id = random.randint(0, N_RP-1)
        lp_id = random.randint(0, N_LP-1)
        vp_id = random.randint(0, N_VP-1)
        
        candidate = [aisles, levels, slots, buf_cap, sp_id, rp_id, lp_id, vp_id]
        
        if feasibility_check(candidate, Slots_min, Slots_max) and candidate not in population:
            population.append(candidate)
        attempts += 1

    return population

def dominates(f1, f2):
    return all(a <= b for a, b in zip(f1, f2)) and any(a < b for a, b in zip(f1, f2))

def dominates_stochastic(avg1, avg2, std1, std2):
    upper1 = [a + factor * s for a, s in zip(avg1, std1)]
    lower2 = [a - factor * s for a, s in zip(avg2, std2)]
    
    return (all(a <= b for a, b in zip(upper1, lower2)) and any(a < b for a, b in zip(upper1, lower2)))

def fast_non_dominated_sort(fitness):
    S = [[] for _ in range(len(fitness))]
    n = [0] * len(fitness)
    fronts = [[]]

    for p in range(len(fitness)):
        for q in range(len(fitness)):
            if dominates(fitness[p], fitness[q]):
                S[p].append(q)
            elif dominates(fitness[q], fitness[p]):
                n[p] += 1

        if n[p] == 0:
            fronts[0].append(p)

    i = 0
    while fronts[i]:
        next_front = []
        for p in fronts[i]:
            for q in S[p]:
                n[q] -= 1
                if n[q] == 0:
                    next_front.append(q)
        i += 1
        fronts.append(next_front)

    return fronts[:-1]

def fast_non_dominated_sort_stochastic(fitness, std):
    S = [[] for _ in range(len(fitness))]
    n = [0] * len(fitness)
    fronts = [[]]

    for p in range(len(fitness)):
        for q in range(len(fitness)):
            if dominates_stochastic(fitness[p], fitness[q], std[p], std[q]):
                S[p].append(q)
            elif dominates_stochastic(fitness[q], fitness[p], std[q], std[p]):
                n[p] += 1

        if n[p] == 0:
            fronts[0].append(p)

    i = 0
    while fronts[i]:
        next_front = []
        for p in fronts[i]:
            for q in S[p]:
                n[q] -= 1
                if n[q] == 0:
                    next_front.append(q)
        i += 1
        fronts.append(next_front)

    return fronts[:-1]

def crowding_distance(front, fitness):
    distance = {i: 0 for i in front}

    for n in range(len(fitness[0])):
        front_sorted = sorted(front, key=lambda i: fitness[i][n])

        distance[front_sorted[0]] = float('inf')
        distance[front_sorted[-1]] = float('inf')

        f_min = fitness[front_sorted[0]][n]
        f_max = fitness[front_sorted[-1]][n]

        if f_max == f_min:
            continue

        for i in range(1, len(front_sorted) - 1):
            prev_f = fitness[front_sorted[i - 1]][n]
            next_f = fitness[front_sorted[i + 1]][n]
            distance[front_sorted[i]] += (next_f - prev_f) / (f_max - f_min)

    return distance

def mutation(population, tested_chrom):
    max_attempts = 5000
    attempts = 0
    mutated_offspring = []
    
    while len(mutated_offspring) < NUM_MUTATIONS and attempts < max_attempts:
        parent = random.choice(population)

        candidate = [
            Creep_Mutation_Dim(parent[0], Aisles_min, Aisles_max),
            Creep_Mutation_Dim(parent[1], Levels_min, Levels_max),
            Creep_Mutation_Dim(parent[2], Columns_min, Columns_max),
            Creep_Mutation_Buf(parent[3], Buf_Cap_min, Buf_Cap_max),
            Random_Resetting(0, N_SP-1),
            Random_Resetting(0, N_RP-1),
            Random_Resetting(0, N_LP-1),
            Random_Resetting(0, N_VP-1),
        ]
        
        attempts += 1
        if tuple(candidate) not in tested_chrom:
            if feasibility_check(candidate, Slots_min, Slots_max) and candidate not in mutated_offspring:
                mutated_offspring.append(candidate)
    
    return mutated_offspring

def recombination(population, tested_chrom):
    max_attempts = 5000
    attempts = 0
    recombined_offspring = []
    
    while len(recombined_offspring) < NUM_RECOMB and attempts < max_attempts:
        parent1, parent2 = random.sample(population, 2)
        
        candidate = [
            Arithmetic_Crossover(parent1[0], parent2[0]),
            Arithmetic_Crossover(parent1[1], parent2[1]),
            Arithmetic_Crossover(parent1[2], parent2[2]),
            Arithmetic_Crossover(parent1[3], parent2[3]),
            Uniform_Crossover(parent1[4], parent2[4]),
            Uniform_Crossover(parent1[5], parent2[5]),
            Uniform_Crossover(parent1[6], parent2[6]),
            Uniform_Crossover(parent1[7], parent2[7])
        ]
        
        attempts += 1
        if tuple(candidate) not in tested_chrom:
            if feasibility_check(candidate, Slots_min, Slots_max) and candidate not in recombined_offspring:
                recombined_offspring.append(candidate)

    return recombined_offspring

def evaluation(chrom):
    Aisles = chrom[0]
    Levels = chrom[1]
    Slots = chrom[2]
    buf_cap = chrom[3]
    Columns = Slots - buf_cap
    store_policy = chrom[4]
    retrieve_policy = chrom[5]
    lift_policy = chrom[6]
    vehicle_policy = chrom[7]
    
    fitness = experiment(Aisles, Levels, Columns, iat_retrieve, iat_store, buf_cap, store_policy, retrieve_policy, vehicle_policy, lift_policy)
    
    return (fitness[0], fitness[1])