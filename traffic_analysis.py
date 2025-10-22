import argparse
import networkx as nx
import matplotlib.pyplot as plt
from utils import helper




# MAIN FUNCTION
def main():
    # PARSER SECTION
    # Creates the parser object in order to read in the passed in arguments and flags.
    #   Utilizes the argparse library to ease the implementation for a working CL structure.
    parser = argparse.ArgumentParser(
        prog="Social Networks and Structural Balance",
        description="This program will help generate randomized graphs and analyze them."
    )

    # Adds additional options and arguments to the parser, accoring to this CL structure:
    #   python ./graph.py ..
    parser.add_argument("input", type=str)
    parser.add_argument("n", type=int)
    parser.add_argument("initial", type=int)
    parser.add_argument("final", type=int)
    parser.add_argument("--plot", action="store_true")

    

    # Parses and gathers the arguments
    args = parser.parse_args()
        
    # Handles if there are not sufficient parameters
    if not args.plot:
        print("--plot is not present. The graph will not be shown.")
    print()
        
    # GRAPH CONSTRUCTION SECTION
    graph = None

        
    if (args.input):
        try:
            graph = nx.read_gml(f"data/{args.input}")
            
        except nx.NetworkXError as e:
            print(f"Error: Could not read the file as a GML graph: {e}")
            print("Please ensure the file is a valid GML format.")
            return
        except FileNotFoundError:
            print(f"File `data/{args.input}` was not found. Please specify an existing .gml file inside the `data/` directory.")
            return
    else:
        print("No --input No graph has been loaded.")

        
    initial = None
    final = None
    n = None
    all_paths = None

    
    if args.initial is not None and args.final is not None and args.n is not None:
        initial = args.initial
        final = args.final
        n = args.n
        all_paths = helper.all_possible_paths(graph, str(initial),str(final)) # get all possbile paths from start node to end node 
        social_optima = helper.compute_social_optima(graph, all_paths,n)
        travel_eq = helper.compute_travel_eq(graph,all_paths,n)
        print(f"Social Optima: {social_optima}")
        print(f"Travel Equilibrium: {travel_eq}")






    # GRAPH PLOTTING SECTION
    if args.plot:
        helper.plot_results(graph, initial, final, travel_eq,True)
        helper.plot_results(graph, initial, final, social_optima,False)
        pass
    else:
        print("There was no graph to be displayed...")



  

  



# Runs the program
if __name__ == "__main__":
  main()
  

'''
CLI Tests:
  python ./traffic_analysis.py traffic.gml 4 0 3 --plot
'''

