#!/usr/bin/env python3

import argparse
from pathlib import Path
import random
import extract_data as ed
import math
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import copy

# Argument Parsing
parser = argparse.ArgumentParser()
parser.add_argument("--dataset"         , type=str  , default="F-n45-k4.vrp")
parser.add_argument("--population"      , type=int  , default=10)
parser.add_argument("--generations"     , type=int  , default=100)
parser.add_argument("--mutation"        , type=float, default=0.5)
parser.add_argument("--crossover"       , type=float, default=0.5)
parser.add_argument("--tournament_size" , type=int  , default=3)
parser.add_argument("--exval"           , type=int  , default=0)
args = parser.parse_args()

basepath = Path(__file__).resolve().parent.parent.parent
filepath = f"{basepath}/EvolutionaryAlgorithmsChug/Database/{args.dataset}"

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
        i, j = random.sample(range(len(individual)), 2)
        individual[i], individual[j] = individual[j], individual[i]
    
    return individual

def tournament_selection(population, fitnesses, tounament_size): # Tournament selection
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
    solutions_over_time = []

    for gen in range(args.generations):

        # Evaluate population
        fitnesses = []
        for individual in population:
            score = fitness(individual, vertices, demands, capacity)
            fitnesses.append(score)

        # Best individual of this generation
        gen_best = min(fitnesses)
        generation_best = population[fitnesses.index(gen_best)]

        # Update global best
        if gen_best < best_cost:
            best_cost = gen_best
            best_solution = generation_best.copy()

        # Store convergence history
        fitness_over_time.append(best_cost)

        # Store this generation's best routes for animation
        generation_routes = split_routes(generation_best, demands, capacity)
        solutions_over_time.append(copy.deepcopy(generation_routes))

        # Create next generation
        new_population = []

        while len(new_population) < args.population:

            parent1 = tournament_selection(
                population, fitnesses, args.tournament_size
            )
            parent2 = tournament_selection(
                population, fitnesses, args.tournament_size
            )

            
            child1, child2 = ox(parent1, parent2, args.crossover)
            child1 = mutate(child1, args.mutation)
            child2 = mutate(child2, args.mutation)

            new_population.extend([child1, child2])

        population = new_population[:args.population]

    # Final best solution
    routes = split_routes(best_solution, demands, capacity)

    return routes, best_cost, fitness_over_time, solutions_over_time

def distance(v1, v2): # Calculates distance between two nodes
    return math.sqrt((v1.x - v2.x)**2+(v1.y - v2.y)**2)

def getvalue(filename): # Get shortest route from .sol file
    base = os.path.splitext(os.path.basename(filename))[0]

    # TODO:
    # enter current working directory
    sol_filename = f"ENTER_FILE_PATH/Database/{base}.sol"

    with open(sol_filename) as f:
        for line in f:
            if line.strip().startswith("Cost"):
                return int(line.split()[1])

def plot_results(vertices, solution, distance_over_time, distance_found, filename, shortest, algo, exval):
    base = os.path.basename(filename) 
    name = os.path.splitext(base)[0] 
    shortest_distance_possible = shortest

    colors = ['blue', 'green', 'red', 'purple', 'cyan', 'grey', 'pink']
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))

    fig.suptitle(f"Vehicle Routing Solution using Genetic Algorithm for: {name}", fontsize=12)
    
    for idx, route in enumerate(solution):
        color = colors[idx % len(colors)]
        x = [vertices[i].x for i in route] + [vertices[route[0]].x]
        y = [vertices[i].y for i in route] + [vertices[route[0]].y]
        axs[0].plot(x, y, marker='o', color=color, label=f"Vehicle {idx+1}")
    
    axs[0].scatter(vertices[0].x, vertices[0].y, color='black', s=100, label='Depot')
    axs[0].set_title("Vehicle Routes", fontsize=10)
    axs[0].legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4, fontsize=6)
    
    # Plot Convergence
    axs[1].plot(distance_over_time)
    axs[1].set_title(f"Convergence", fontsize=10)
    axs[1].set_xlabel("Generation")
    axs[1].set_ylabel("Distance")
    axs[1].text(0.5, -0.25, f"Shortest Distance possible: {shortest_distance_possible}", transform=axs[1].transAxes, ha='center')
    axs[1].text(0.5, -0.30, f"Shortest Distance found: {distance_found:.0f}", transform=axs[1].transAxes, ha='center')

    plt.tight_layout()
    
    #TODO:
    # Enter your current working directory
    # directory is another term for file path

    plt.savefig(f"ENTER_YOUR_FILE_PATH_HERE/Day4/{algo}_{name}_test_no_{exval}.png")
    #plt.savefig(f"/home/patryksiutkowski/GitHub/EvolutionaryAlgorithmsChug/Day4/{algo}_{name}_test_no_{exval}.png")


def animate_results(vertices, solutions_over_time, distance_over_time, distance_found, filename, shortest, algo, exval):

    base = os.path.basename(filename)
    name = os.path.splitext(base)[0]

    colors = ['blue', 'green', 'red', 'purple', 'cyan', 'grey', 'pink']

    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle(
        f"Vehicle Routing Solution using Genetic Algorithm for: {name}",
        fontsize=12
    )

    def update(frame):

        #TODO:
        # Clear previous drawings
        # using .clear()
        ...


        solution = solutions_over_time[frame]

        # Draw vehicle routes
        for idx, route in enumerate(solution):
            color = colors[idx % len(colors)]

            x = [vertices[i].x for i in route] + [vertices[route[0]].x]
            y = [vertices[i].y for i in route] + [vertices[route[0]].y]

            axs[0].plot(
                x, y,
                marker='o',
                color=color,
                label=f"Vehicle {idx+1}"
            )

        axs[0].scatter(vertices[0].x,vertices[0].y, color='black', s=100, label='Depot')
        axs[0].set_title(f"Vehicle Routes (Generation {frame})")
        axs[0].legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4, fontsize=6)

        # Keep axis fixed so animation doesn't jump        
        xs = [v.x for v in vertices]
        ys = [v.y for v in vertices]
        axs[0].set_xlim(min(xs)-5, max(xs)+5)
        axs[0].set_ylim(min(ys)-5, max(ys)+5)

        # Convergence plot
        axs[1].plot(range(frame + 1), distance_over_time[:frame + 1], color='blue')

        axs[1].set_xlim(0, len(distance_over_time))
        axs[1].set_ylim(min(distance_over_time) * 0.95, max(distance_over_time) * 1.05)

        axs[1].set_title("Convergence")
        axs[1].set_xlabel("Generation")
        axs[1].set_ylabel("Distance")

        axs[1].text(0.5, -0.25, f"Shortest Distance possible: {shortest}", transform=axs[1].transAxes, ha='center')
        axs[1].text(0.5, -0.30, f"Best Distance Found: {distance_found:.0f}", transform=axs[1].transAxes, ha='center')

    ani = FuncAnimation(fig, update,frames=len(solutions_over_time), interval=100, repeat=False)
    
    # TODO:
    # Enter your working directory
    #
    output = f"ENTER_FILE_PATH_HERE/Day4/{algo}_{name}_test_no_{exval}.mp4"

    ani.save(output, writer="ffmpeg", fps=10)

if __name__ == "__main__":
    vertices, demands, capacity = ed.extract_data(filepath)
    solution, best_cost, fitness_over_time, solutions_over_time = genetic_algorithm(vertices, demands, capacity)
    shortest = getvalue(filepath)
    
    plot_results(vertices, solution, fitness_over_time, best_cost, filepath, shortest, "ga", args.exval)
    animate_results(vertices, solutions_over_time, fitness_over_time, best_cost, filepath, shortest, "ga", args.exval)