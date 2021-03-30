"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching

This script contains the entry point to the program (the code in
`__main__.py` calls `main()`). Your solution starts here!
"""

import sys
import json

# If you want to separate your code into separate files, put them
# inside the `search` directory (like this one and `util.py`) and
# then import from them like this:
from search.util import *

def main():
    try:
        with open(sys.argv[1]) as file:
            data = json.load(file)
    except IndexError:
        print("usage: python3 -m search path/to/input.json", file=sys.stderr)
        sys.exit(1)

    # TODO:
    # Find and print a solution to the board configuration described
    # by `data`.
    # Why not start by trying to print this configuration out using the
    # `print_board` helper function? (See the `util.py` source code for
    # usage information).

    board = parse_board(data)

    lower_pieces = parse_pieces(data,"lower")
    upper_pieces = parse_pieces(data,"upper")

    target_dist_dict = make_target_distances(board)
    routing = target_assign(upper_pieces,lower_pieces,target_dist_dict, board)
    routing_new = convert_targets(data, routing)

    print(routing_new)

    board = parse_board(data)
    print_board(board)

    calculated_nodes = {}
    node_queue = [(0, data, -1, -1, 0)] #queues of nodes in form of (node_id, board_state, parent_node_id, score, depth). 

    find_solution(node_queue, calculated_nodes, routing_new, target_dist_dict)