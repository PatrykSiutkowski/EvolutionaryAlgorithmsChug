#!/usr/bin/env python3

import argparse
from pathlib import Path
import numpy as np
import random
import matplotlib.pyplot as plt
import os
from extract_data import extract_data

# Argument Parsing
parser = argparse.ArgumentParser()
parser.add_argument("--dataset"    , type=str  , default="F-n45-k4.vrp")
parser.add_argument("--generations", type=int  , default=100)
parser.add_argument("--ants"       , type=int  , default=10)
parser.add_argument("--alpha"      , type=float, default=1.0) # Pheromone importance: Controls how much influence the pheromone trail has on an ant's decision.
parser.add_argument("--beta"       , type=float, default=1.0) # Heuristic importance: Controls how much importance is given to the heuristic
parser.add_argument("--rho"        , type=float, default=0.5) # Evaporation rate    : Determines how quickly the pheromone evaporates.
parser.add_argument("--h"          , type=float, default=0.2) # Control parameter   : balances exploitation and exploration
parser.add_argument("--Q"          , type=float, default=2.0) # Pheromone deposit   : Scaling factor for how much pheromone is laided by each ant based on solution quality.
parser.add_argument("--exval"      , type=int  , default=99)
args = parser.parse_args()

basepath = Path(__file__).resolve().parent.parent.parent

# TODO:
# Enter your directory for the Database
filepath = f"ENTER_YOUR_FILE_PATH_HERE/Database/{args.dataset}"

def compute_distance_matrix(vertices): # Builds matrix for weights used to initalised pheromones
    n = len(vertices)
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                # TODO:
                # write code that computes dx and dy from vertices[i]
                # then calculates the D[i, j] from np.hypot using dx, dy
                ...
    return D

def fitness(D, solution): # Defines fitness as the sum of all routes
    total_distance = 0

    for route in solution:
        route_distance = 0
        for i in range(len(route) - 1):

            # TODO:
            # Complete these variables
            #
            from_node = ...
            to_node = ...
            route_distance += ...
        total_distance += route_distance
    return total_distance

def compute_candidate_list(D, k=10): # Candidate list
    candidate_list = []

    for i in range(len(D)):
        sorted_indices = np.argsort(D[i]) # Sort nodes by distance from node i
        nearest_neighbours = sorted_indices[1:k+1] # Exclude the node itself (first element) and take next k neighbours
        candidate_list.append(nearest_neighbours)
    return candidate_list

def construct_solution(tau, eta, demand, capacity, candidate_list, alpha, beta, rho, h):
    n = len(tau)
    depot = 0
    unvisited = set(range(n))
    unvisited.remove(depot)

    routes = []

    while unvisited:
        route = [depot]
        load = 0
        current = depot

        while True:
            feasible = []

            for node in unvisited:
                if load + demand[node] <= capacity:
                    feasible.append(node)
            
            if not feasible:
                break

            candidates = []

            for node in candidate_list[current]:
                if node in feasible:
                    candidates.append(node)
                    
            if not candidates:
                candidates = feasible
            
            # Exploitation
            if random.random() <= h: 
                next_node = max(candidates, key=lambda j: (tau[current][j] ** alpha) * (eta[current][j] ** beta))

            # Exploration
            else: 
                probs = []
                for j in candidates:
                    val = (tau[current][j] ** alpha) * (eta[current][j] ** beta)
                    probs.append(val)
                probs = np.array(probs)
                probs /= probs.sum()
                next_node = np.random.choice(candidates, p=probs)

            route.append(next_node)
            unvisited.remove(next_node)
            load += demand[next_node]

            local_update(tau, current, next_node, rho) 

            current = next_node

        route.append(depot)
        routes.append(route)

    return routes

def route_cost(route, D):
    total_distance = 0

    for i in range(len(route) - 1):
        from_node = route[i]
        to_node = route[i + 1]

        # TODO:
        # Calculate the total_distance
        # This can be done using the variables above
        ... 

    return total_distance

def local_update(tau, current, next_node, rho): # Local pheromone update as per equation
    tau[current][next_node] = (1 - rho) * tau[current][next_node] + rho

def global_update(tau, solutions, fitnesses, rho, Q, sigma=3):
    
    tau *= (1 - rho) # Evaporation

    ranked = sorted(zip(solutions, fitnesses), key=lambda x: x[1]) # Rank ants

    for mu, (solution, cost) in enumerate(ranked[:sigma-1], start=1): # Rank-based pheromone contribution (Δτ_ij)
        weight = (sigma - mu)

        for route in solution:
            for i in range(len(route) - 1):
                a, b = route[i], route[i + 1]

                delta = weight * (Q / cost)

                tau[a][b] += delta
                tau[b][a] += delta

    best_sol, best_cost = ranked[0] # Elitist update equivalent to Δτ_ij*

    for route in best_sol:
        for i in range(len(route) - 1):
            a, b = route[i], route[i + 1]

            delta_star = sigma * (Q / best_cost)

            tau[a][b] += delta_star
            tau[b][a] += delta_star

def ant_solver(vertices, demand, capacity, alpha, beta, rho, h, Q, ants):
    D = compute_distance_matrix(vertices)
    eta = 1 / (D + 1e-10) # 1e-10 present to prevent divison by zero

    candidate_list = compute_candidate_list(D)

    best_solution = None
    best_cost = float('inf')
    history = []

    for it in range(args.generations):
        solutions = []
        fitnesses = []

        for _ in range(ants):
            solution = construct_solution(eta, demand, capacity, candidate_list, alpha, beta, rho, h)
            
            cost = fitness(D, solution)
            solutions.append(solution)
            fitnesses.append(cost)

            if cost < best_cost:
                best_solution = solution
                best_cost = cost

        global_update(solutions, fitnesses, rho, Q)
        history.append(best_cost)
    
    return best_solution, best_cost, history

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
    plt.savefig(f"ENTER_YOUR_FILE_PATH_HERE/AntColony/Results/{algo}_{name}_test_no_{exval}.png")

def getvalue(filename): # Get shortest route from .sol file
    base = os.path.splitext(os.path.basename(filename))[0]

    # TODO:
    # Enter your directory for the Database
    sol_filename = f"ENTER_YOUR_FILE_PATH_HERE/Database/{base}.sol"

    with open(sol_filename) as f:
        for line in f:
            if line.strip().startswith("Cost"):
                return int(line.split()[1])

if __name__ == "__main__":
    vertices, demand, capacity = extract_data(filepath)
    best_solution, best_cost, history = ant_solver(vertices, demand, capacity, args.alpha, args.beta, args.rho, args.h, args.Q, args.ants)
    shortest = getvalue(filepath)

    print(f"The shortest route found has a distnce of: {shortest}")
    plot_results(vertices, best_solution, history, best_cost, filepath, shortest, algo="aco", exval=args.exval)