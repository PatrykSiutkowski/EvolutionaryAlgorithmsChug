#!/usr/bin/env python3

import argparse
from pathlib import Path
import random
import extract_data as ed
import math
import os

# Argument Parsing
parser = argparse.ArgumentParser()
parser.add_argument("--dataset"         , type=str  , default="F-n45-k4.vrp")
parser.add_argument("--population"      , type=int  , default=10)
parser.add_argument("--generations"     , type=int  , default=1000)
parser.add_argument("--mutation"        , type=float, default=0.5)
parser.add_argument("--crossover"       , type=float, default=0.5)
parser.add_argument("--tournament_size" , type=int  , default=3)
args = parser.parse_args()

basepath = Path(__file__).resolve().parent.parent.parent
filepath = f"{basepath}/EvolutionaryAlgorithmsChug/Dataset/{args.dataset}"

def distance(v1, v2): # Calculates distance between two nodes
    return math.sqrt((v1.x - v2.x)**2+(v1.y - v2.y)**2)

def getvalue(filename): # Get shortest route from .sol file
    base = os.path.splitext(os.path.basename(filename))[0]
    sol_filename = f"{basepath}/EvolutionaryAlgorithmsChug/Dataset/{base}.sol"

    with open(sol_filename) as f:
        for line in f:
            if line.strip().startswith("Cost"):
                return int(line.split()[1])

def split_routes(individual, demands, capacity): # Decode CVRP routes
    routes = []
    route = [0]
    load = 0

    for customer in individual:
        d = demands[customer]

        if load + d > capacity:
            route.append(0)
            routes.append(route)
            route = [0]
            load = 0

        route.append(customer)
        load += d

    route.append(0)
    routes.append(route)

    return routes

def fitness(individual, vertices, demands, capacity):
    routes = split_routes(individual, demands, capacity)

    total = 0
    for route in routes:
        for i in range(len(route) - 1):
            total += distance(vertices[route[i]], vertices[route[i+1]])

    return total

def ox(parent1, parent2, crossover_rate): # OX crossover
    if random.random() > crossover_rate:
        return parent1.copy(), parent2.copy()

    size = len(parent1)
    p1, p2 = sorted(random.sample(range(size), 2))

    def create_child(a, b):
        child = [-1] * size
        child[p1:p2] = a[p1:p2]

        fill = []

        for x in b:
            if x not in child:
                fill.append(x)

        idx = 0

        for i in range(size):
            if child[i] == -1:
                child[i] = fill[idx]
                idx += 1
        
        return child
    
    return create_child(parent1, parent2), create_child(parent2, parent1)

def mutate(individual, mutation_rate): # Mutation (swap)
    if random.random() < mutation_rate:
        # TODO:
        # Finish this function so that it mutates the individual
        # This is accomplishes by sampling from i and j then
        # swapping their placement in the chromosome
        # then returning the mutated individual
        ...
    

def tournament_selection(population, fitnesses, tounament_size): # Tournament selection
    # TODO:
    # create a variable that ramdomly samples the population alongside their fitnesses
    # then sorts them
    # 
    #
    ...
    
    selected = random.sample(list(zip(population, fitnesses)), tounament_size)
    selected.sort(key=lambda x: x[1])
    
    return selected[0][0]

def generate_population(num_customers, population_size): # Initial population

    population = []
    base = list(range(1, num_customers))  # exclude depot (0)

    for _ in range(population_size):
        perm = base.copy()
        random.shuffle(perm)
        population.append(perm)

    return population

def genetic_algorithm(vertices, demands, capacity):
    population = generate_population(len(vertices), args.population)

    best_solution = None
    best_cost = float("inf")
    fitness_over_time = []

    for gen in range(args.generations):

        fitnesses = []

        for individual in population:
            score = fitness(individual, vertices, demands, capacity)
            fitnesses.append(score)

        # Track best
        gen_best = min(fitnesses)
        if gen_best < best_cost:
            best_cost = gen_best
            best_solution = population[fitnesses.index(gen_best)]

        fitness_over_time.append(best_cost)

        new_population = [] # New generation

        while len(new_population) < args.population:

            parent1 = tournament_selection(population, fitnesses, args.tournament_size)
            parent2 = tournament_selection(population, fitnesses, args.tournament_size)

            child1, child2 = ox(parent1, parent2, args.crossover)
            child1 = mutate(child1, args.mutation)
            child2 = mutate(child2, args.mutation)

            new_population.extend([child1, child2])

        population = new_population[:args.population]

    routes = split_routes(best_solution, demands, capacity)
    return routes, best_cost, fitness_over_time

if __name__ == "__main__":
    vertices, demands, capacity = ed.extract_data(filepath)
    solution, best_cost, fitness_over_time = genetic_algorithm(vertices, demands, capacity)
    shortest = getvalue(filepath)
    print(shortest)