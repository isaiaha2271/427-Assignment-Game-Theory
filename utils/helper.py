import networkx as nx
import numpy as np
import itertools
import matplotlib.pyplot as plt
import math

# intialize flow amount for every set of edges in graph
def intialize_flows(G):
    flows = {(u, v): 0 for u, v in G.edges()}
    return flows

def compute_social_optima(G, paths,n):
    num_paths = len(paths)
    vehicles_per_path = n/num_paths
    flow_dict = intialize_flows(G)


    #update flow dict to evenly distribute vehciles for each
    for path in paths:
        for i in range(len(path)-1):
            u = path[i]
            v = path[i+1]
            flow_dict[(u,v)] += vehicles_per_path
        
    convergence_threshold = 0.001
    iteration_limit = 100
    iter1 = 0

    #adjust network flows iteratively
    while iter1 < iteration_limit:
              

        marg_cost_dict = {}
        #compute marginal cost for a given path in the graph
        for u,v in flow_dict:
            a = G[u][v]['a']
            marg_cost_dict[(u,v)] = compute_travel_time(G,u,v,flow_dict[(u,v)]) +flow_dict[(u,v)]*a
        

        path_costs = {}

        #compute travel time for each path and keep track of path with smallest cost
        min_path = None
        for path in paths:  
            cost = sum(marg_cost_dict[(path[i],path[i+1])] for i in range(len(path)-1))
            path_costs[tuple(path)] = cost
            if not min_path:
                min_path= (path,cost)
            else:
                if cost < min_path[1]:
                    min_path = (path,cost)

        shortest_path,min_cost = min_path

        #check if all nonzero paths are roguhly equal
        converged = True 
        for path in path_costs:
            if sum(flow_dict[(path[i],path[i+1])] for i in range(len(path)-1))> 0: #checking paths with flow >0 for equilibirum 
                if abs(path_costs[tuple(path)]-min_cost) > convergence_threshold:
                    converged = False
                    break
        if converged: #all paths are within 0.001 cost difference(they are roughly same), thus social optimum reach 
            break
                

        #shift flow towards shortest path
        step_size = 0.5
        direction_flow = {edge:0 for edge in flow_dict}
        flow_per_path = n*step_size
        for i in range(len(shortest_path)-1):
            edge = (shortest_path[i], shortest_path[i+1])
            direction_flow[edge] += flow_per_path


        

        # Update flows for each edge using weighted average
        for edge in flow_dict:
            flow_dict[edge] = (1-step_size)*flow_dict[edge]+step_size*direction_flow[edge]
        
        iter1+=1
    return flow_dict



#compute travel equilibrium for a given graph, paths, and number of cars
def compute_travel_eq(G,paths, n):
    num_paths = len(paths)
    vehicles_per_path = n / num_paths
    flow_dict = intialize_flows(G)


    #update flow dict to evenly distribute vehciles for each
    for path in paths:
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]
            flow_dict[(u, v)] += vehicles_per_path
    convergence_threshold = 0.001
    iteration_limit = 100
    iter1 = 0

    #adjust network flows iteratively
    while iter1 < iteration_limit:
        path_costs = {}

        # compute travel time for each path and keep track of path with smallest cost
        min_path = None
        for path in paths:
            cost = path_cost(G, path, flow_dict)
            path_costs[tuple(path)] = cost
            if not min_path:
                min_path = (path, cost)
            else:
                if cost < min_path[1]:
                    min_path = (path, cost)
        shortest_path, min_cost = min_path

        # check if all nonzero paths are roguhly equal
        converged = True
        for path in path_costs:
            if (
                sum(flow_dict[(path[i], path[i + 1])] for i in range(len(path) - 1)) > 0
            ):  # checking paths with flow >0 for equilibirum
                if abs(path_costs[tuple(path)] - min_cost) > convergence_threshold:
                    converged = False
                    break
        if converged:
            break
                


        #shift flow towards shortest path
        step_size = 0.5
        direction_flow = {edge:0 for edge in flow_dict}
        flow_per_path = n*step_size

        for i in range(len(shortest_path)-1):
            edge = (shortest_path[i], shortest_path[i+1])
            direction_flow[edge] += flow_per_path


       

        # Update flows for each edge using weighted average
        for edge in flow_dict:
            flow_dict[edge] = (1-step_size)*flow_dict[edge]+step_size*direction_flow[edge]

        iter1 += 1
    return flow_dict


def plot_results(G, flow_dict=None, eq = False):
    pos = nx.spring_layout(G)
    plt.figure(figsize=(12, 8))
    
    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=500)
    nx.draw_networkx_labels(G, pos)
    
    # Draw edges with weights and flows
    edge_labels = {}
    for u, v in G.edges():
        a = G[u][v]['a']
        b = G[u][v]['b']
        flow = f" Drivers {flow_dict[(u,v)]:.0f}" if flow_dict else ""
        edge_labels[(u, v)] = f'{a}x + {b}: {flow}'
    
    nx.draw_networkx_edges(G, pos, edge_color='black', arrows=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_color='red')

    
    if eq:
        plt.title("Travel Equilibrium Network Flow Graph")
    else:
        plt.title("Social Optima Network Flow Graph")


    plt.axis('off')
    plt.show()


# obtain all possible paths in grpah
def all_possible_paths(G, start, end):
    return list(nx.all_simple_paths(G, start, end))


# calculate travel time for x cars to travel on edge (u,v)
def compute_travel_time(G, u, v, x):
    a = G[u][v]["a"]
    b = G[u][v]["b"]
    return a * x + b


# compute total travel time along a path given list of edges of the path
def path_cost(G, path, flows):
    total = 0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]  # get pair of nodes making the edge
        total += compute_travel_time(
            G, u, v, flows[(u, v)]
        )  # increment total with travel time of the edge given its current number of cars
    return total



#round flows in given flow_dictionary do get discrete number of drivers for each edge that mathces input of n drivers
def round_flows_to_integers(flow_dict, n):
    
    #Round down all flows
    floored_flows = {edge: math.floor(flow) for edge, flow in flow_dict.items()}

    #Calculate how many drivers we have left to assign
    total_flow = sum(floored_flows.values())
    remaining = n - total_flow  # how many drivers still unassigned

    # If we need to assign more drivers, give them to edges with the largest fractional parts
    if remaining > 0:
        fractional_parts = {
            edge: flow_dict[edge] - math.floor(flow_dict[edge]) for edge in flow_dict
        }
        # Sort edges by fractional part (descending)
        sorted_edges = sorted(fractional_parts.keys(), key=lambda e: fractional_parts[e], reverse=True)

        for i in range(remaining):
            edge = sorted_edges[i % len(sorted_edges)]
            floored_flows[edge] += 1

    #If rounding caused too many drivers , remove from edges with smallest nonzero flows
    elif remaining < 0:
        nonzero_edges = [e for e, f in floored_flows.items() if f > 0]
        nonzero_edges = sorted(nonzero_edges, key=lambda e: floored_flows[e])  # smallest first

        for i in range(abs(remaining)):
            if i < len(nonzero_edges):
                floored_flows[nonzero_edges[i]] -= 1

    # Guarantee non-negativity
    for edge in floored_flows:
        floored_flows[edge] = max(0, floored_flows[edge])

    return floored_flows


