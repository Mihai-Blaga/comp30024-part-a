"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching

This module contains some helper functions for printing actions and boards.
Feel free to use and/or modify them to help you develop your program.
"""
import copy
from itertools import combinations
from itertools import permutations
import random

next_id = 1
MAX_INT = 99999

def compare_states(s1):
    """
    Function used as the comparator in the unvisited_nodes queue.
    Order by number of pieces (smaller is better), 
    tie-breaking on scores (smaller is better), 
    tie-breaking on depth (deeper is better)
    """
    return (len((s1[1])["lower"]), s1[3], -s1[4])

def find_solution(unvisited_nodes, visited_nodes, targets, target_dists):
    """
    Main body of the program. Finds a path to a finished state given targetting dictionary.
    """
    unvisited_nodes.sort(key = compare_states)
    node = unvisited_nodes.pop(0)

    curr_id = node[0]
    state = copy.deepcopy(node[1])
    curr_cost = node[3] - sum_dist_to_targets(state, targets, target_dists)
    depth = node[4]

    visited_nodes[curr_id] = node

    #checking for collisions
    new_lower = []
    for l_piece in state["lower"]:
        flag = True
        for u_piece in state["upper"]:
            if (l_piece[1] == u_piece[1] and l_piece[2] == u_piece[2]):
                if live_hex(u_piece[1], u_piece[2], l_piece[0], u_piece[0]):
                    flag = False
        
        if flag:
            new_lower.append(l_piece)

    state["lower"] = new_lower

    #end state check
    if (finished(state)):
        print_all_nodes(curr_id, visited_nodes)
        return

    #checking if reached target
    for piece in targets.keys():
        if ((state["upper"][piece][1],state["upper"][piece][2]) == targets[piece][0]):
            if (len(targets[piece]) > 1):
                targets[piece] = targets[piece][1:]
            else:
                #Retargetting
                
                lower_pieces = parse_pieces(state,"lower")
                upper_pieces = parse_pieces(state,"upper")
        
                board = parse_board(state)
                #target_dist_dict = make_target_distances(lower_pieces,board)

                routing = target_assign(upper_pieces,lower_pieces,target_dists, board)
                targets = convert_targets(state, routing)  


    moves = potential_moves(state, targets, target_dists)

    for move in moves:
        global next_id
        pot_score = score(move, targets, curr_cost, target_dists)
        unvisited_nodes.append((next_id, move, curr_id, pot_score, depth+1))
        next_id = next_id + 1


    return find_solution(unvisited_nodes, visited_nodes, targets, target_dists)

def finished(state):
    """
    For a given board state, confirms it is in an accepted "finished" state based on absence of any lower pieces.
    """
    return (len(state["lower"]) == 0)

def print_all_nodes(curr_id, visited_nodes):
    """
    Recursive function that prints all moves leading up to a given position.
    """
    if (curr_id == 0):
        return 1
    else:
        parent_id = visited_nodes[curr_id][2]
        depth = print_all_nodes(parent_id, visited_nodes) #prints all moves leading to this position.

        print_moves(visited_nodes[parent_id][1], visited_nodes[curr_id][1], depth)
        return depth + 1

def print_moves(prev, curr, depth):
    """
    Given two board states, find differences between them and figure out the moves
    """
    old_locations = prev["upper"]
    new_locations = curr["upper"]
    for i in range(0, len(old_locations)):
        old_spot = old_locations[i]
        new_spot = new_locations[i]
        
        if (calc_dist(old_spot[1], old_spot[2], new_spot[1], new_spot[2]) == 1):
            print_slide(depth, old_spot[1], old_spot[2], new_spot[1], new_spot[2])

        elif(calc_dist(old_spot[1], old_spot[2], new_spot[1], new_spot[2]) > 1):
            print_swing(depth, old_spot[1], old_spot[2], new_spot[1], new_spot[2])

    return

def potential_moves(state, targets, target_dists):
    """
    Returns list of all potential move states that are better than the current. [pot_board_states]
    """
    pieces = state["upper"]
    adj_positions = adj_loc(state)
    moves = []
    using_loc = {}

    #dictionary of all lower piece positions to be used for live checking
    lower_pos = {}
    for piece in state["lower"]:
        lower_pos[(piece[1], piece[2])] = piece[0]


    #simplifying adj_positions into only positions >= curr and moves that won't kill the pieces.
    for key in adj_positions.keys():
        new_list = []
        old_loc = (pieces[key][1], pieces[key][2])

        dist_board = target_dists[targets[key][0]]
        old_dist = dist_board[old_loc]
        
        for loc in adj_positions[key]:
            live_flag = True
            if ((loc[0], loc[1]) in lower_pos):
                live_flag = live_hex(loc[0], loc[1], lower_pos[(loc[0], loc[1])], state["upper"][key][0].upper())
            
            new_dist = dist_board[loc]
            if (new_dist <= old_dist and live_flag):
                new_list.append(loc)
        
        adj_positions[key] = new_list

    #making list of all possible combinations of moves
    for loc in adj_positions[0]:
        using_loc[0] = loc
        move = copy.deepcopy(state)
        (move["upper"])[0][1] = loc[0]
        (move["upper"])[0][2] = loc[1]

        if (len(adj_positions.keys()) > 1):
            for loc_1 in adj_positions[1]:
                if (loc_1 != using_loc[0]):
                    using_loc[1] = loc_1
                    move = copy.deepcopy(move)
                    (move["upper"])[1][1] = loc_1[0]
                    (move["upper"])[1][2] = loc_1[1]

                    if (len(adj_positions.keys()) > 2):
                        for loc_2 in adj_positions[2]:
                            if (loc_2 != using_loc[0] and loc_2 != using_loc[1]):
                                move = copy.deepcopy(move)
                                using_loc[2] = loc_2
                                (move["upper"])[2][1] = loc_2[0]
                                (move["upper"])[2][2] = loc_2[1]
                                moves.append(move)
                    else:
                        moves.append(move)
        else:
            moves.append(move)
    
    return moves

def adj_loc(state):
    """
    Returns list of all potential moves for each moveable piece. Format {attacker_num: [moves]}
    """
    pieces = state["upper"]
    moves = {}
    for i in range(0, len(pieces)):
        hex_moves = []
        for j in range(0, len(pieces)):

            #Looking for swing moves (for piece one hex away)
            if (i != j and (calc_dist(pieces[i][1], pieces[i][2], pieces[j][1], pieces[j][2]) == 1)):
                swing_moves = adj_hex(pieces[j][1], pieces[j][2])
                hex_moves = hex_moves + swing_moves

        hex_moves = hex_moves + adj_hex(pieces[i][1], pieces[i][2])
        hex_moves.append((pieces[i][1], pieces[i][2]))
        hex_moves = list(set(hex_moves)) #remove duplicates

        moves[i] = hex_moves

    return moves


def adj_hex(r1, q1):
    """
    Returns list of all adjacent hexes to target hex
    """
    hexes = []
    if (valid_hex(r1 - 1, q1)):
        hexes.append((r1 - 1, q1))
    if (valid_hex(r1 + 1, q1)):
        hexes.append((r1 + 1, q1))
    if (valid_hex(r1, q1 - 1)):
        hexes.append((r1, q1 - 1))
    if (valid_hex(r1, q1 + 1)):
        hexes.append((r1, q1 + 1))
    if (valid_hex(r1 - 1, q1 + 1)):
        hexes.append((r1 - 1, q1 + 1))
    if (valid_hex(r1 + 1, q1 - 1)):
        hexes.append((r1 + 1, q1 - 1))

    return hexes
    

def score(move, targets, prev_cost, target_dists):
    """
    Calculates the score of the current board state.
    """
    score = prev_cost
    sum = sum_dist_to_targets(move, targets, target_dists)

    return score + sum

def sum_dist_to_targets(state, targets, target_dists):
    """
    Calculates the sum of distances from pieces to their target locations
    """
    pieces = state["upper"]
    sum = 0
    for i in range(0, len(pieces)):
        dist_board = target_dists[targets[i][0]]
        piece_location = (pieces[i][1], pieces[i][2])
        sum = sum + dist_board[piece_location]
    
    return sum

def convert_targets(state, targets):
    """
    Converts from target dictionary of form dict[piece_location] = [target_location_list]
    to dict[piece_number_in_state_definition] = [target_location_list]
    Useful because the piece_location is constantly changing.
    """
    converted = {}
    i = 0

    for piece in state["upper"]:
        converted[i] = targets[(piece[1], piece[2])]
        i = i + 1
    
    return converted

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
    Outputs a dictionary of the form {(r, q): distance from target hex}
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
    """
    Recursively calculate distances. Calculates distances around #.
    """
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


def make_target_distances(curr_board_state):
    """
    Returns target_distance_dict.
    The Keys for the dict are the target coordinate
    The value is the dist_dict from dist_board_dict
    """
    target_distance_dict = {}
    for i in range(-4, 5):
        for j in range(-4, 5):
            target_distance_dict[(i, j)] = dist_board_block(i, j, curr_board_state)
    return target_distance_dict


def target_assign(upper_pieces, lower_pieces, target_distances, board_in):
    """
    Returns Target_dict. 
    The Keys are starting coordinates of attacker peices
    The Values are a list of target coordinates, to be attacked in order
    Eg target_dict[(0,1)] = [(0,2),(1,2)]
    
    This Function matches attacking pieces to their valid targets,
    then combines three target_dicts into final output.
    """

    target_dict = {}
    
    rock_targets = target_assign_two(upper_pieces[0],lower_pieces[2],target_distances, board_in)
    paper_targets = target_assign_two(upper_pieces[1],lower_pieces[0],target_distances, board_in)
    scissors_targets = target_assign_two(upper_pieces[2],lower_pieces[1],target_distances, board_in)

    target_dict.update(rock_targets)
    target_dict.update(paper_targets)
    target_dict.update(scissors_targets)

    return target_dict


def target_assign_two(attackers_list, targets_list, target_distances, board_in):
    """
    Returns targets in same format as target_dict.
    Input is Attackers and their targets. EG Upper Scissors and Lower Paper
    Assumes Targets >=1
    """
    targets = {}

    if len(attackers_list) == 0:
        return targets
    
    elif len(targets_list) == 0:
        #If no targets, move to nearby valid hex without dying. 
        for attacker in attackers_list:
            current_r = attacker[0][0]
            current_q = attacker[0][1]
            for i_r in range(-1,2):
                for i_q in range(-1,2):
                    if (i_r != 0) or (i_q != 0):
                        if valid_hex(current_r + i_r, current_q + i_q):
                            if live_hex(current_r + i_r, current_q + i_q, board_in[(current_r+i_r,current_q+i_q)], attacker[1]):
                                targets[attacker[0]] = [(current_r + i_r, current_q + i_q)]
        return targets
    

    else:
        #More Targets than Attackers

        #Dictionary Of Dictionaries of Route Lengths
        attacker_route_length = {}

        #Removes types from targets_list
        target_simple = simplify_targets(targets_list)


        #target_lists is a list containing all combinations of targets as tuples(?)
        target_lists = []
        for i in range (1,len(target_simple)+1):
            x = combinations(target_simple,i)
            for n in x:
                target_lists.append(n)

        #For Each Attacker, find the "shortest" path length for each combination of targets
        for attacker in attackers_list:
            attacker_route_length[attacker[0]] = {}
            attacker_route_length[attacker[0]][()] = [(),0]
            for bloop in target_lists:
                perms = list(permutations(bloop))
                perm_i = 0
                num_perms = len(perms)
                best = make_attacker_route_length(attacker[0],bloop, target_distances)
                while (perm_i < 50) and (perm_i < num_perms):
                    random_i = random.randint(0,num_perms-1)
                    temp = make_attacker_route_length(attacker[0], perms[random_i], target_distances)
                    if temp[1] < best[1]:
                        best = temp
                    perm_i = perm_i + 1

                attacker_route_length[attacker[0]][bloop] = best


        #Make list of all attacker_route combinations
        all_valid_combs = make_valid_combinations(target_simple, len(attackers_list))

        #Assume the First Combination is the shortest
        shortest_comb = all_valid_combs[0]
        shortest_longest_len = 0
        for i in range(len(attackers_list)):
            dist = sum_len(attackers_list[i][0],all_valid_combs[0][i],target_distances)
            if dist > shortest_longest_len:
                shortest_longest_len = dist

        #Test The rest of the combinations to find the(a) actual shortest
        for comb in all_valid_combs:
            longest_len = 0
            for i in range(len(attackers_list)):
                dist = attacker_route_length[attackers_list[i][0]][comb[i]][1]
                #dist = sum_len(attackers_list[i][0],comb[i],target_distances)
                if dist > longest_len:
                    longest_len = dist

            if longest_len < shortest_longest_len:
                shortest_longest_len = longest_len
                shortest_comb = comb
        
        #Using shortest comb, add to targets
        for i in range(len(attackers_list)):
            if len(shortest_comb[i]) > 0:
                targets[attackers_list[i][0]] = attacker_route_length[attackers_list[i][0]][shortest_comb[i]][0]
            else:
                #Target closest
                dists =[]
                for target in targets_list:
                    dists.append(target_distances[target[0]][attackers_list[i][0]])
                min_dist = min(dists)
                c = dists.index(min_dist)
                targets[attackers_list[i][0]] = [targets_list[c][0]]
            

        return targets


def simplify_targets(target_list):
    """
    Removes type from target_list
    """
    output = []
    for target in target_list:
        output.append(target[0])
    return output


def make_valid_combinations(target_coordinates, num_attackers_left):
    """
    This function returns all possible ways the targets can be sorted to the number of attackers
    Should return (attackers)^targets combinations
    EG target 1 can go to attacker 1, 2, or 3
    Target 2 can go to attacker 1, 2, or 3 ...


    Returns a list of lists.
    The sublists contains tuples
    The tuples contain combinations of targets

    """
    if num_attackers_left == 1:
        output3 = tuple(target_coordinates)
        output2 = [output3]
        output = [output2]
        return output
    
    else:
        output = []
        for i in range(len(target_coordinates) + 1):
            x = combinations(target_coordinates,i)
            for n in x:
                new = target_coordinates.copy()
                for m in n:
                    new.remove(m)
                ob = make_valid_combinations(new, num_attackers_left-1)
                for thing in ob:
                    thing2 = thing.copy()
                    thing2.append(n)
                    output.append(thing2)
        return output
 


def make_attacker_route_length(attacker_coords, targets_list, target_distances):
    """
    Takes a list of targets and an attacker
    returns "shortest" path from starting point

    Inserts targets one at a time to minimise route length

    """
    if len(targets_list) > 1:
        attack_order = make_attacker_route_length(attacker_coords, targets_list[1:], target_distances)[0]
        
        dist_list =[]
        for i in range(len(attack_order)+1):
            
            attack_list = attack_order.copy()
            attack_list.insert(i,targets_list[0])
            dist_list.append(sum_len(attacker_coords,attack_list,target_distances))
        smallest = min(dist_list)
        i=dist_list.index(smallest)
        output1 = attack_order.copy()
        output1.insert(i,targets_list[0])
        output = [output1]
        output.append(smallest)
        # I can't remember why output has the smallest in it
        return output

    else:
        #Base Case, return target
        attack_order = [targets_list[0]]
        output = [attack_order]
        b = target_distances[targets_list[0]][attacker_coords]
        output.append(b)
        return output
    
def sum_len(attacker_coords, attack_list, target_distances):
    big_list = list(attack_list)
    big_list.insert(0,attacker_coords)
    total = 0

    for i in range(1,len(big_list)):
       
        total = total + target_distances[big_list[i]][big_list[i-1]]
    return total



def dist_board_block(r, q, curr_board_state):
    """
    Outputs a dictionary of the form (r, q): distance from target hex, taking into account blockers.
    """
    dist_dict = {}
    global MAX_INT

    dist_dict = recursive_dist_calc(r, q, curr_board_state, dist_dict, -1)

    for i in range(-4, 5):
        for j in range(-4, 5):
            if (valid_hex(i, j) and curr_board_state[(i,j)] == '#'):
                dist_dict[(i, j)] = MAX_INT

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
