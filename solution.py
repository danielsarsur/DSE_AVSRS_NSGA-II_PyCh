import os
import csv
import numpy as np
from genetic_algorithm import *
from config import *

if __name__ == "__main__":

    log_all = 'log_all.csv'
    if not os.path.exists(log_all):
        with open(log_all, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f, delimiter=';').writerow(['generation', 'chromo', 'store_avg', 'store_std', 'retrieve_avg', 'retrieve_std'])
    
    log_gen = 'log_generations.csv'
    if not os.path.exists(log_gen):
        with open(log_gen, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f, delimiter=';').writerow(['generation', 'chromo', 'store_avg', 'store_std', 'retrieve_avg', 'retrieve_std'])

    log_pareto_gen = 'log_pareto_generations.csv'
    if not os.path.exists(log_pareto_gen):
        with open(log_pareto_gen, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f, delimiter=';').writerow(['generation', 'chromo', 'store_avg', 'store_std', 'retrieve_avg', 'retrieve_std'])

    log_pareto = 'log_pareto.csv'
    if not os.path.exists(log_pareto):
        with open(log_pareto, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f, delimiter=';').writerow(['generation', 'chromo', 'store_avg', 'store_std', 'retrieve_avg', 'retrieve_std'])

    try:
        population = Initial_Pop()
        pareto_population = []
        tested_chrom = set()
        tested_chrom.update(tuple(p) for p in population)

        fitness_results = np.array([[evaluation(ind) for ind in population] for _ in range(REPETITIONS)])
        fitness_values = np.mean(fitness_results, axis=0)
        fitness_std = np.std(fitness_results, axis=0)

        for c, fit, std in zip(population, fitness_values, fitness_std):
            with open(log_gen, 'a', newline='', encoding='utf-8') as f:
                csv.writer(f, delimiter=';').writerow(["0", str(c).replace(',', ''), str(fit[0]).replace('.', ','), str(std[0]).replace('.', ','), str(fit[1]).replace('.', ','), str(std[1]).replace('.', ',')])
        for c, fit, std in zip(population, fitness_values, fitness_std):
            with open(log_all, 'a', newline='', encoding='utf-8') as f:
                csv.writer(f, delimiter=';').writerow(["0", str(c).replace(',', ''), str(fit[0]).replace('.', ','), str(std[0]).replace('.', ','), str(fit[1]).replace('.', ','), str(std[1]).replace('.', ',')])

        for gen in range(NUM_GENERATIONS):
            start_gen = time.time()
            
            offspring_mut = mutation(population, tested_chrom)
            tested_chrom.update(tuple(p) for p in offspring_mut)

            offspring_rec = recombination(population, tested_chrom)
            tested_chrom.update(tuple(p) for p in offspring_rec)
            
            offspring = offspring_mut + offspring_rec

            if not offspring:
                break

            offspring_fitness_results = np.array([[evaluation(ind) for ind in offspring] for _ in range(REPETITIONS)])
            offspring_fitness_values = np.mean(offspring_fitness_results, axis=0)
            offspring_fitness_std = np.std(offspring_fitness_results, axis=0)

            for c, fit, std in zip(offspring, offspring_fitness_values, offspring_fitness_std):
                with open(log_all, 'a', newline='', encoding='utf-8') as f:
                    csv.writer(f, delimiter=';').writerow([gen+1, str(c).replace(',', ''), str(fit[0]).replace('.', ','), str(std[0]).replace('.', ','), str(fit[1]).replace('.', ','), str(std[1]).replace('.', ',')])

            combined_pop = np.vstack([population, offspring])
            combined_fit = np.vstack([fitness_values, offspring_fitness_values])
            combined_std = np.vstack([fitness_std, offspring_fitness_std])
            
            fronts = fast_non_dominated_sort_stochastic(combined_fit, combined_std)

            pareto_front_idx = fronts[0]
            pareto_population = [combined_pop[i] for i in pareto_front_idx]
            pareto_fitness = [combined_fit[i] for i in pareto_front_idx]
            pareto_std = [combined_std[i] for i in pareto_front_idx]

            for c, fit, std in zip(pareto_population, pareto_fitness, pareto_std):
                with open(log_pareto_gen, 'a', newline='', encoding='utf-8') as f:
                    csv.writer(f, delimiter=';').writerow([gen+1, str(c).replace(',', ''), str(fit[0]).replace('.', ','), str(std[0]).replace('.', ','), str(fit[1]).replace('.', ','), str(std[1]).replace('.', ',')])

            new_population = []
            new_fitness = []
            new_fitness_std = []

            for front in fronts:
                if len(new_population) + len(front) <= POP_SIZE:
                    for idx in front:
                        new_population.append(combined_pop[idx])
                        new_fitness.append(combined_fit[idx])
                        new_fitness_std.append(combined_std[idx])
                else:
                    distances = crowding_distance(front, combined_fit)
                    sorted_front = sorted(front, key=lambda i: distances[i], reverse=True)

                    for idx in sorted_front:
                        if len(new_population) < POP_SIZE:
                            new_population.append(combined_pop[idx])
                            new_fitness.append(combined_fit[idx])
                            new_fitness_std.append(combined_std[idx])
                        else:
                            break
                    break

            population = list(new_population)
            fitness_values = np.array(new_fitness)
            fitness_std = np.array(new_fitness_std)

            for c, fit, std in zip(population, fitness_values, fitness_std):
                with open(log_gen, 'a', newline='', encoding='utf-8') as f:
                    csv.writer(f, delimiter=';').writerow([gen+1, str(c).replace(',', ''), str(fit[0]).replace('.', ','), str(std[0]).replace('.', ','), str(fit[1]).replace('.', ','), str(std[1]).replace('.', ',')])

        pareto_idx = fast_non_dominated_sort_stochastic(fitness_values, fitness_std)[0]

        pareto_population = [population[i] for i in pareto_idx]
        pareto_fitness = [fitness_values[i] for i in pareto_idx]
        pareto_std = [fitness_std[i] for i in pareto_idx]

        for c, fit, std in zip(pareto_population, pareto_fitness, pareto_std):
            with open(log_pareto, 'a', newline='', encoding='utf-8') as f:
                csv.writer(f, delimiter=';').writerow([NUM_GENERATIONS+1, c, str(fit[0]).replace('.', ','), str(std[0]).replace('.', ','), str(fit[1]).replace('.', ','), str(std[1]).replace('.', ',')])

    except Exception as e:
        print(f"ERROR: {e}")
