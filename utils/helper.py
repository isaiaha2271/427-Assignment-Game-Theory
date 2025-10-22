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
    
    social_cost = 0
    total_potential_power = 0
    
    # Draw edges with weights and flows
    edge_labels = {}
    for u, v in G.edges():
        a = G[u][v]['a']
        b = G[u][v]['b']
        drivers = int(flow_dict[(u,v)]) if flow_dict else None
        flow = f" Drivers {drivers}" if drivers else ""
        # TRAVEL TIME AND SOCIAL COST
        travel_time = drivers * ((a * drivers) + b)
        travel_time_label = f"Travel Time {travel_time}" 
        social_cost += travel_time
        # POTENTIAL POWER
        potential_power = np.sum(x for x in range(1, drivers + 1)) if travel_time else 0
        potential_power_label = f"Potential Power {potential_power}"
        total_potential_power += potential_power
        
        # LABEL
        edge_labels[(u, v)] = f'{a}x + {b}: {flow}\n{travel_time_label}\n{potential_power_label}'
    
    nx.draw_networkx_edges(G, pos, edge_color='black', arrows=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_color='red')
    
    plt.title("Network Flow Graph")
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
