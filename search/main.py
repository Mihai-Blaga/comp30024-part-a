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

    target_dist_dict = make_target_distances(lower_pieces,board)
    routing = target_assign(upper_pieces,lower_pieces,target_dist_dict)

    print(routing)
    print_board(routing,compact=False)
    #print_board(board, compact=False, ansi=True)
    print_board(dist_board_block(4,0, board), ansi=True)