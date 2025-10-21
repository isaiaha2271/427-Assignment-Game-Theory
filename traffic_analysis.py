import argparse
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from itertools import islice
from utils import helper
import os


# MAIN FUNCTION
def main():
    # PARSER SECTION
    # Creates the parser object in order to read in the passed in arguments and flags.
    #   Utilizes the argparse library to ease the implementation for a working CL structure.
    parser = argparse.ArgumentParser(
        prog="Social Networks and Structural Balance",
        description="This program will help generate randomized graphs and analyze them.",
    )
    # Adds additional options and arguments to the parser, according to this CL structure:
    #   python ./traffic_analysis.py digraph_file.gml n initial final --plot
    parser.add_argument("input", type=str)
    parser.add_argument("n", type=int)
    parser.add_argument("initial", type=int)
    parser.add_argument("final", type=int)
    parser.add_argument("--plot", action="store_true")
    # Parses and gathers the arguments
    args = parser.parse_args()

    # DEBUG
    print(args.input, args.n, args.initial, args.final, args.plot)

    # Handles if there are not sufficient parameters
    if not args.plot:
        print("--plot is not present. The graph will not be shown.")
    print()

    # GRAPH CONSTRUCTION SECTION
    graph = None
    # Determines if the input is valid GML
    if args.input:
        try:
            graph = nx.read_gml(f"{args.input}")
        except nx.NetworkXError as e:
            print(f"Error: Could not read the file as a GML graph: {e}")
            print("Please ensure the file is a valid GML format.")
            return
        except FileNotFoundError:
            print(
                f"File `{args.input}` was not found. Please specify an existing .gml file inside the `data/` directory."
            )
            return
    else:
        print("No --input No graph has been loaded.")

    # MAIN SECTION
    initial = None
    final = None
    n = None

    if args.n is not None and args.initial is not None and args.final is not None:
        initial = args.initial
        final = args.final
        n = args.n

        paths = helper.all_possible_paths(graph, initial, final)
        social_optima = helper.compute_social_optima(graph, initial, final, n)
        travel_eq = helper.compute_travel_eq(graph, paths, n)
        print(f"Social Optima: {social_optima}")
        print(f"Travel Equilibrium: {travel_eq}")
        
        # GRAPH PLOTTING SECTION
        if args.plot:
            helper.plot_results(graph, travel_eq)
        else:
            print("There was no graph to be displayed...")

    else:
        print(
            "One of the following was not provided: n, initial, or final. Please run the program according to this structure:"
        )
        print("\tpython ./traffic_analysis.py digraph_file.gml n initial final --plot")


# Runs the program
if __name__ == "__main__":
    main()

"""
CLI Tests:
  python ./traffic_analysis.py traffic.gml 4 0 3 --plot
"""
