"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching

This module contains some helper functions for printing actions and boards.
Feel free to use and/or modify them to help you develop your program.
"""
def valid_hex(r, q):
    """
    For any hexagon (r,q) returns True if it would 
    appear on a standard 5-sided hexagonal board.
    """
    if (r > 4 or r < -4 or q > 4 or q < -4):
        return False
    minimum_val = max(-4, -4-q)
    maximum_val = min(4, 4-q)
    return ((minimum_val <= r) and (maximum_val >= r))

def live_hex(r, q, target_piece, original_piece):
    """
    returns true if the piece will survive moving to the specified hex
    """
    #maps pieces from rock, paper, scissors or blank to a ordinal number for maths.
    piece_map = {'r': 0, 'P': 1, 's': 2, 'R': 3, 'p': 4, 'S': 5, '': -2}

    if (target_piece == '#' or not (valid_hex(r,q))):
        return False

    original_piece = piece_map[original_piece]
    target_piece = piece_map[target_piece]

    if (original_piece != -2 and target_piece != -2):
        return not (((original_piece + 1) % 6) == target_piece or ((original_piece + 4) % 6) == target_piece)

    return True
        

def calc_dist(r1, q1, r2, q2):
    """
    Returns distance between hexes (r1, q1) and (r2, q2)
    """

    if((not valid_hex(r1, q1)) or (not valid_hex(r2, q2))):
        return -1
    
    dist = max(abs(r1-r2), abs(q1-q2), abs((r1+q1) - (r2+q2)))

    return dist

def dist_board(r, q):
    """
    DEBUGGING FUNCTION
    Outputs a dictionary of the form (r, q): distance from target hex.
    """
    if (not valid_hex(r, q)):
        return -1

    dist_dict = {}

    for i in range(-4, 5):
        for j in range(-4, 5):
            if (valid_hex(i, j)):
                dist_dict[(i, j)] = calc_dist(i, j, r, q)

    return dist_dict

def recursive_dist_calc(r, q, curr_board, dist_dict, cost):
    if (not valid_hex(r, q) or not live_hex(r, q, curr_board[(r, q)], '')):
        return dist_dict
    
    if (not ((r,q) in dist_dict) or dist_dict[(r,q)] > (cost + 1)):
        dist_dict[(r,q)] = cost + 1
        dist_dict = recursive_dist_calc(r+1, q, curr_board, dist_dict, cost+1)
        dist_dict = recursive_dist_calc(r, q+1, curr_board, dist_dict, cost+1)
        dist_dict = recursive_dist_calc(r+1, q-1, curr_board, dist_dict, cost+1)
        dist_dict = recursive_dist_calc(r-1, q+1, curr_board, dist_dict, cost+1)
        dist_dict = recursive_dist_calc(r-1, q, curr_board, dist_dict, cost+1)
        dist_dict = recursive_dist_calc(r, q-1, curr_board, dist_dict, cost+1)

    return dist_dict

def parse_pieces(data,up_or_low):
    """
    Input data, and either "upper" or "lower" for the relevant team.
    Returns pieces_list, which has three lists
    pieces_list[0] is a list of rock pieces,
    pieces_list[1] is a list of paper pieces,
    pieces_list[2] is a list of scissors pieces.
    eg pieces_list[2][0] = [(1,2),"s"]
    """
    pieces_list = []

    pieces_list.append([])
    pieces_list.append([])
    pieces_list.append([])

    pieces = data[up_or_low]
    for piece in pieces:
        if piece[0] == "r":
            pieces_list[0].append([(piece[1],piece[2]),piece[0]])
        elif piece[0] == "p":
            pieces_list[1].append([(piece[1],piece[2]),piece[0]])
        else:
            pieces_list[2].append([(piece[1],piece[2]),piece[0]])

    return pieces_list


def make_target_distances(lower_pieces, curr_board_state):
    """
    Returns target_distance_dict.
    The Keys for the dict are the coordinates of lower pieces
    The value is the dist_dict from dist_board_dict
    """

    target_distance_dict = {}
    for min_list in lower_pieces:
        for piece in min_list:
            target_distance_dict[piece[0]] = dist_board_block(piece[0][0], piece[0][1], curr_board_state)

    return target_distance_dict


def target_assign(upper_pieces, lower_pieces, target_distances):
    """
    Returns Target_dict. 
    The Keys are starting coordinates of attacker peices
    The Values are a list of target coordinates, to be attacked in order
    Eg target_dict[(0,1)] = [(0,2),(1,2)]
    
    This Function matches attacking pieces to their valid targets,
    then combines three target_dicts into final output.
    """

    target_dict = {}
    
    rock_targets = target_assign_two(upper_pieces[0],lower_pieces[2],target_distances)
    paper_targets = target_assign_two(upper_pieces[1],lower_pieces[0],target_distances)
    scissors_targets = target_assign_two(upper_pieces[2],lower_pieces[1],target_distances)

    target_dict.update(rock_targets)
    target_dict.update(paper_targets)
    target_dict.update(scissors_targets)

    return target_dict


def target_assign_two(attackers_list, targets_list, target_distances):
    """
    Returns targets in same format as target_dict.
    Input is Attackers and their targets. EG Upper Scissors and Lower Paper
    """
    targets = {}

    if len(attackers_list) == 0:
        return targets

    elif len(attackers_list) >= len(targets_list):
        # LONGEST SHORTEST PATH
        bloop = []
        targets_left = [i for i in range(len(targets_list))]
        attackers_left = [i for i in range(len(attackers_list))]
        #Generate bloop
        #bloop is a list of lists, where the bloop[i] is a list belonging to target i
        #the values of the sub-list are the distances to target j. bloop[i][j]
        for target in targets_left:
            temp_list =[]
            for attacker in attackers_left:
                temp_list.append(target_distances[targets_list[target][0]][attackers_list[attacker][0]])
            bloop.append(temp_list)


        while len(targets_left) > 0:
            #Set First target and first attacker as max_min
            #Set min_target_row as the first row
            #min_target_row is the row with the highest minimum value
            max_min_target_dist = bloop[targets_left[0]][attackers_left[0]]
            min_target_row = targets_left[0]

            # Find the max_min value, and the row that it is in
            for row in targets_left:
                row_min = bloop[row][attackers_left[0]]
                for attacker in attackers_left:
                    if bloop[row][attacker] < row_min:
                        row_min = bloop[row][attacker]
                if row_min > max_min_target_dist:
                    max_min_target_dist = row_min
                    min_target_row = row

            # Get the attacker num from the first position of max_min in bloop[row]
            for attacker in attackers_left:
                if bloop[min_target_row][attacker] == max_min_target_dist:
                    attacker_num = attacker
                    break
            
            # Add to output
            targets[attackers_list[attacker_num][0]] = [targets_list[row][0]]

            #Remove target and Attacker from remaining list
            targets_left.remove(row)
            attackers_left.remove(attacker_num)

        # All targets should now have an attacker
        
        #Assign remaining attackers to closest target
        # Optional, can be changed later
        while len(attackers_left) > 0:
            min_dist = bloop[0][attackers_left[0]]
            min_target = 0
            for i_target in range(len(targets_list)):
                if bloop[i_target][attackers_left[0]] < min_dist:
                    min_dist = bloop[i_target][attackers_left[0]]
                    min_target = i_target

            targets[attackers_list[attackers_left[0]][0]] = [targets_list[min_target][0]]
            del attackers_left[0]
        
        return targets


    else:
        #More Targets than Attackers
        #TO DO

        return targets


def dist_board_block(r, q, curr_board_state):
    """
    DEBUGGING FUNCTION
    Outputs a disctionary of the form (r, q): distance from target hex, taking into account blockers.
    """
    dist_dict = {}

    dist_dict = recursive_dist_calc(r, q, curr_board_state, dist_dict, -1)

    for i in range(-4, 5):
        for j in range(-4, 5):
            if (valid_hex(i, j) and curr_board_state[(i,j)] == '#'):
                dist_dict[(i, j)] = '#'

    return dist_dict

def parse_board(data):
    """
    DEBUGGING FUNCTION
    Outputs a dictionary of the form (r, q): piece-code.
    """
    board_dict = {}

    upper = data["upper"]
    lower = data["lower"]
    block = data["block"]

    for i in range(-4, 5):
        for j in range(-4, 5):
            if (valid_hex(i, j)):
                board_dict[(i, j)] = ''

    for piece in upper:
        board_dict[(piece[1], piece[2])] = piece[0].upper()

    for piece in lower:
        board_dict[(piece[1], piece[2])] = piece[0]

    for piece in block:
        board_dict[(piece[1], piece[2])] = "#"

    return board_dict

#----- vv FUNCTIONS THAT CAME WITH THE SKELETON CODE vv -----

def print_slide(t, r_a, q_a, r_b, q_b, **kwargs):
    """
    Output a slide action for turn t of a token from hex (r_a, q_a)
    to hex (r_b, q_b), according to the format instructions.

    Any keyword arguments are passed through to the print function.
    """
    print(f"Turn {t}: SLIDE from {(r_a, q_a)} to {(r_b, q_b)}", **kwargs)


def print_swing(t, r_a, q_a, r_b, q_b, **kwargs):
    """
    Output a swing action for turn t of a token from hex (r_a, q_a)
    to hex (r_b, q_b), according to the format instructions.
    
    Any keyword arguments are passed through to the print function.
    """
    print(f"Turn {t}: SWING from {(r_a, q_a)} to {(r_b, q_b)}", **kwargs)


def print_board(board_dict, message="", compact=True, ansi=False, **kwargs):
    """
    For help with visualisation and debugging: output a board diagram with
    any information you like (tokens, heuristic values, distances, etc.).

    Arguments:

    board_dict -- A dictionary with (r, q) tuples as keys (following axial
        coordinate system from specification) and printable objects (e.g.
        strings, numbers) as values.
        This function will arrange these printable values on a hex grid
        and output the result.
        Note: At most the first 5 characters will be printed from the string
        representation of each value.
    message -- A printable object (e.g. string, number) that will be placed
        above the board in the visualisation. Default is "" (no message).
    ansi -- True if you want to use ANSI control codes to enrich the output.
        Compatible with terminals supporting ANSI control codes. Default
        False.
    compact -- True if you want to use a compact board visualisation,
        False to use a bigger one including axial coordinates along with
        the printable information in each hex. Default True (small board).
    
    Any other keyword arguments are passed through to the print function.

    Example:

        >>> board_dict = {
        ...     ( 0, 0): "hello",
        ...     ( 0, 2): "world",
        ...     ( 3,-2): "(p)",
        ...     ( 2,-1): "(S)",
        ...     (-4, 0): "(R)",
        ... }
        >>> print_board(board_dict, "message goes here", ansi=False)
        # message goes here
        #              .-'-._.-'-._.-'-._.-'-._.-'-.
        #             |     |     |     |     |     |
        #           .-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
        #          |     |     | (p) |     |     |     |
        #        .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
        #       |     |     |     | (S) |     |     |     |
        #     .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
        #    |     |     |     |     |     |     |     |     |
        #  .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
        # |     |     |     |     |hello|     |world|     |     |
        # '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
        #    |     |     |     |     |     |     |     |     |
        #    '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
        #       |     |     |     |     |     |     |     |
        #       '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
        #          |     |     |     |     |     |     |
        #          '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
        #             | (R) |     |     |     |     |
        #             '-._.-'-._.-'-._.-'-._.-'-._.-'
    """
    if compact:
        template = """# {00:}
#              .-'-._.-'-._.-'-._.-'-._.-'-.
#             |{57:}|{58:}|{59:}|{60:}|{61:}|
#           .-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
#          |{51:}|{52:}|{53:}|{54:}|{55:}|{56:}|
#        .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
#       |{44:}|{45:}|{46:}|{47:}|{48:}|{49:}|{50:}|
#     .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
#    |{36:}|{37:}|{38:}|{39:}|{40:}|{41:}|{42:}|{43:}|
#  .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
# |{27:}|{28:}|{29:}|{30:}|{31:}|{32:}|{33:}|{34:}|{35:}|
# '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#    |{19:}|{20:}|{21:}|{22:}|{23:}|{24:}|{25:}|{26:}|
#    '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#       |{12:}|{13:}|{14:}|{15:}|{16:}|{17:}|{18:}|
#       '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#          |{06:}|{07:}|{08:}|{09:}|{10:}|{11:}|
#          '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#             |{01:}|{02:}|{03:}|{04:}|{05:}|
#             '-._.-'-._.-'-._.-'-._.-'-._.-'"""
    else:
        template = """# {00:}
#                  ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#                 | {57:} | {58:} | {59:} | {60:} | {61:} |
#                 |  4,-4 |  4,-3 |  4,-2 |  4,-1 |  4, 0 |
#              ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#             | {51:} | {52:} | {53:} | {54:} | {55:} | {56:} |
#             |  3,-4 |  3,-3 |  3,-2 |  3,-1 |  3, 0 |  3, 1 |
#          ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#         | {44:} | {45:} | {46:} | {47:} | {48:} | {49:} | {50:} |
#         |  2,-4 |  2,-3 |  2,-2 |  2,-1 |  2, 0 |  2, 1 |  2, 2 |
#      ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#     | {36:} | {37:} | {38:} | {39:} | {40:} | {41:} | {42:} | {43:} |
#     |  1,-4 |  1,-3 |  1,-2 |  1,-1 |  1, 0 |  1, 1 |  1, 2 |  1, 3 |
#  ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
# | {27:} | {28:} | {29:} | {30:} | {31:} | {32:} | {33:} | {34:} | {35:} |
# |  0,-4 |  0,-3 |  0,-2 |  0,-1 |  0, 0 |  0, 1 |  0, 2 |  0, 3 |  0, 4 |
#  `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
#     | {19:} | {20:} | {21:} | {22:} | {23:} | {24:} | {25:} | {26:} |
#     | -1,-3 | -1,-2 | -1,-1 | -1, 0 | -1, 1 | -1, 2 | -1, 3 | -1, 4 |
#      `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
#         | {12:} | {13:} | {14:} | {15:} | {16:} | {17:} | {18:} |
#         | -2,-2 | -2,-1 | -2, 0 | -2, 1 | -2, 2 | -2, 3 | -2, 4 |
#          `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
#             | {06:} | {07:} | {08:} | {09:} | {10:} | {11:} |
#             | -3,-1 | -3, 0 | -3, 1 | -3, 2 | -3, 3 | -3, 4 |   key:
#              `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'     ,-' `-.
#                 | {01:} | {02:} | {03:} | {04:} | {05:} |       | input |
#                 | -4, 0 | -4, 1 | -4, 2 | -4, 3 | -4, 4 |       |  r, q |
#                  `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'         `-._,-'"""
    # prepare the provided board contents as strings, formatted to size.
    ran = range(-4, +4+1)
    cells = []
    for rq in [(r,q) for r in ran for q in ran if -r-q in ran]:
        if rq in board_dict:
            cell = str(board_dict[rq]).center(5)
            if ansi:
                # put contents in bold
                cell = f"\033[1m{cell}\033[0m"
        else:
            cell = "     " # 5 spaces will fill a cell
        cells.append(cell)
    # prepare the message, formatted across multiple lines
    multiline_message = "\n# ".join(message.splitlines())
    # fill in the template to create the board drawing, then print!
    board = template.format(multiline_message, *cells)
    print(board, **kwargs)
