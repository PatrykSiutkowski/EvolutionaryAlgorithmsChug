#!/usr/bin/env python3

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def extract_data(filename):
    coords = {}
    demands = {}
    capacity = None
    depot = None
    section = None

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("COMMENT"):
                continue

            if line.startswith("CAPACITY"):
                capacity = int(line.split(":")[1])
                continue

            if line == "NODE_COORD_SECTION":
                section = "coords"
                continue
            elif line == "DEMAND_SECTION":
                section = "demands"
                continue
            elif line == "DEPOT_SECTION":
                section = "depot"
                continue
            elif line == "EOF":
                break

            if section == "coords":
                i, x, y = line.split()
                coords[int(i)] = Node(float(x), float(y))

            elif section == "demands":
                i, d = line.split()
                demands[int(i)] = int(d)

            elif section == "depot":
                if line != "-1":
                    depot = int(line)

    # ---- FIX INDEXING HERE ----
    n = len(coords)

    # vertices[0] = depot
    vertices = [coords[depot]]
    for i in range(1, n + 1):
        if i != depot:
            vertices.append(coords[i])

    # demands aligned with vertices
    demand_list = [0]
    for i in range(1, n + 1):
        if i != depot:
            demand_list.append(demands[i])

    return vertices, demand_list, capacity