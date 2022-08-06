# Name:         Kyle Kesler
# Course:       CSC 480
# Instructor:   Daniel Kauffman
# Assignment:   Tile Driver II
# Term:         Spring 2021

import random
from typing import Callable, List, Tuple, Set

import tiledriver


def is_solvable(tiles: Tuple[int, ...]) -> bool:
    """
    Return True if the given tiles represent a solvable puzzle and False
    otherwise.

    >>> is_solvable((3, 2, 1, 0))
    True
    >>> is_solvable((0, 2, 1, 3))
    False
    """
    _, inversions = _count_inversions(list(tiles))
    width = int(len(tiles) ** 0.5)
    if width % 2 == 0:
        row = tiles.index(0) // width
        return (row % 2 == 0 and inversions % 2 == 0 or
                row % 2 == 1 and inversions % 2 == 1)
    else:
        return inversions % 2 == 0


def _count_inversions(ints: List[int]) -> Tuple[List[int], int]:
    """
    Count the number of inversions in the given sequence of integers (ignoring
    zero), and return the sorted sequence along with the inversion count.

    This function is only intended to assist |is_solvable|.

    >>> _count_inversions([3, 7, 1, 4, 0, 2, 6, 8, 5])
    ([1, 2, 3, 4, 5, 6, 7, 8], 10)
    """
    if len(ints) <= 1:
        return ([], 0) if 0 in ints else (ints, 0)
    midpoint = len(ints) // 2
    l_side, l_inv = _count_inversions(ints[:midpoint])
    r_side, r_inv = _count_inversions(ints[midpoint:])
    inversions = l_inv + r_inv
    i = j = 0
    sorted_tiles = []
    while i < len(l_side) and j < len(r_side):
        if l_side[i] <= r_side[j]:
            sorted_tiles.append(l_side[i])
            i += 1
        else:
            sorted_tiles.append(r_side[j])
            inversions += len(l_side[i:])
            j += 1
    sorted_tiles += l_side[i:] + r_side[j:]
    return (sorted_tiles, inversions)


def is_valid_move(tiles: Tuple[int, ...], mv: str, width: int) -> bool:
    """Return True if the move is valid and False otherwise"""
    zero = tiles.index(0)
    # determine if blank space is on the edge of the puzzle
    row = int(zero / width)
    col = int(zero % width)
    b_row = width - 1
    r_col = b_row

    # determine if the move attempts to move the blank space off the puzzle
    if (not row and mv == 'J') or (not col and mv == 'L'):
        return False
    elif ((row == b_row) and (mv == "K")) or ((col == r_col) and (mv == "H")):
        return False
    return True


def is_opposing_move(prev_move: str) -> str:
    """
    Returns a string containing a specific combination of the characters 'H',
    'J', 'K', 'L' representing the possible moves that would not undo the
    previous move
    """
    moves = "HJKL"
    # dictionary to hold the opposite of each move
    opposite = {'H': 'L', 'J': 'K', 'K': 'J', 'L': 'H'}
    if prev_move != "":
        # remove/return a string of moves that doesn't undo previous move
        return moves.replace(opposite.get(prev_move), '')
    return moves


def move_tile(tiles: list, move: str, width: int) -> list:
    """
    Returns a list of the tiles after swapping the blank tile with the tile
    corresponding to the move direction
    """
    # dictionary of moves with the corresponding distance to move the tile to
    move_sizes = {"H": 1, "J": -width, "K": width, "L": -1}
    dist = move_sizes.get(move)
    # swapping the blank tile (0) with the tile in the position to be moved to
    zero_loc = tiles.index(0)
    replace_tile = tiles[zero_loc + dist]
    tiles[zero_loc + dist] = 0
    tiles[zero_loc] = replace_tile
    return tiles


def get_frontier_states(state: Tuple[int, ...], prev_move: str,
                            explored: Set[Tuple], width: int) -> List[list]:
    """
    Using the previous move, determines possible moves that are valid and
    non-opposing to create frontier states. Adds frontier states that have not
    been explored yet to the priority queue.
    """
    frontier_states = []
    # obtain list of possible non-opposing moves
    possible_moves = is_opposing_move(prev_move)
    for i in possible_moves:
        # determine if move is valid (would it move blank tile off puzzle)
        if is_valid_move(state, i, width):
            # swap the blank tile with tile in move direction
            moved = tuple(move_tile(list(state), i, width))
            if moved not in explored:
                frontier_states.append([moved, i])
    return frontier_states


def random_restart(width: int) -> List[int]:
    """Returns a list representing a randomly shuffled solvable tile puzzle"""
    # create ordered list of tiles based off of width
    tiles = list(range(width**2))
    random.shuffle(tiles)
    # ensure tile configuration is solvable
    while not is_solvable(tuple(tiles)):
        random.shuffle(tiles)
    return tiles


def acceptance_probability(old_conflicts: int, new_conflicts: int,
                                                        t: float) -> float:
    """
    Return acceptable probability statistic determined from an exponential
    function using simulated annealing temperature
    """
    e = 2.718281828459045
    if new_conflicts > old_conflicts:
        return 1
    return round(e**(- (new_conflicts - old_conflicts) / t), 10)


def random_neighbor(frontier: List[list],
                            explored: Set[Tuple]) -> Tuple[Tuple[int], str]:
    """
    Returns a random frontier state that has not been explored along with its
    corresponding move
    """
    max_states = 4
    i = 0
    # get initial random state
    random.shuffle(frontier)
    state = frontier[0][0]
    prev_move = frontier[0][1]
    # if state is already explored move to next state
    while state in explored and i <= max_states:
        random.shuffle(frontier)
        state = frontier[0][0]
        prev_move = frontier[0][1]
        i += 1
    # if all states explored return random
    return state, prev_move


def simulated_annealing(tiles: Tuple[int, ...], min_lc: int,
                                            width: int) -> Tuple[int, ...]:
    """
    Use simulated annealing algorithm to determine tile state with maximum
    number of linear conflicts. If no maximum reaches the required minimum
    number of linear conflicts in the max number of iterations return the
    current state. Otherwise the state with the required linear conflicts is
    returned.
    """
    explored = set()
    state = tiles
    explored.add(state)
    prev_move = ""
    max_iter = 500
    rand_num = [.05, .1, .14, .22, .29, .32, .4, .45, .5, .58, .64, .7, .8, .89]
    # get initial number of linear conflicts
    lc = tiledriver.Heuristic._get_linear_conflicts(state, width)
    for i in range(max_iter):
        # determine temperature for acceptance probability
        temp = max(0.001, min(1.0, 1.0 - (i / max_iter)))
        # get all possible frontier states. if none break and return
        frontier_states = get_frontier_states(state, prev_move, explored, width)
        if not frontier_states:
            break
        # choose a frontier state at random
        new_state, prev_move = random_neighbor(frontier_states, explored)
        new_lc = tiledriver.Heuristic._get_linear_conflicts(new_state, width)
        # if number of linear conflicts meets requirements return
        if new_lc >= min_lc:
            state = new_state
            break
        explored.add(new_state)
        # determine acceptance prob. and compare with random number
        # (in beggining there is a higher chance of choosing a worse state
        if new_lc >= lc:
            random.shuffle(rand_num)
            if acceptance_probability(lc, new_lc, temp) > rand_num[0]:
                state, lc = new_state, new_lc
    return tuple(state)


def conflict_tiles(width: int, min_lc: int) -> Tuple[int, ...]:
    """
    Create a solvable shuffled puzzle of the given width with a minimum number
    of linear conflicts (ignoring Manhattan distance).

    >>> tiles = conflict_tiles(3, 5)
    >>> tiledriver.Heuristic._get_linear_conflicts(tiles, 3)
    5
    """
    lc = 0
    while lc < min_lc:
        # generate a random set of tiles
        tiles = tuple(random_restart(width))
        # use simulated annealing to find tile arrangment with a specific
        # number of linear conflicts
        tiles = simulated_annealing(tiles, min_lc, width)
        lc = tiledriver.Heuristic._get_linear_conflicts(tiles, width)
    return tiles


def get_frontier_states_s(state: Tuple[int, ...], prev_move: str,
                                                    width: int) -> List[list]:
    """
    Using the previous move, determines possible moves that are valid and
    non-opposing to create frontier states.
    """
    frontier_states = []
    # obtain list of possible non-opposing moves
    possible_moves = is_opposing_move(prev_move)
    for i in possible_moves:
        # determine if move is valid (would it move blank tile off puzzle)
        if is_valid_move(state, i, width):
            # swap the blank tile with tile in move direction
            moved = tuple(move_tile(list(state), i, width))
            frontier_states.append([moved, i])
    return frontier_states


def best_state(frontier: List[list]) -> Tuple[Tuple[int], str, int]:
    """
    Returns the best state, move corresponding to that state, and max_path to
    solution from the choices in frontier.
    """
    cur_max_path = 0
    # iterate through each frontier state
    for state_mv in frontier:
        # use path length to solution to evaluate states
        new_path = tiledriver.Heuristic.get(state_mv[0])
        if new_path >= cur_max_path:
            m_state, m_prev_move = state_mv[0], state_mv[1]
            cur_max_path = new_path
    return m_state, m_prev_move, cur_max_path


def uphill_climbing(tiles: Tuple[int, ...], min_len: int,
                                    width: int) -> Tuple[Tuple[int, ...], int]:
    """
    Use uphill climbing algorithm to find the required minimum optimal solution
    length. Returns the tile state and length of optimal solution. If a solution
    that fits the min_len requirement is not found a local max is returned.
    """
    cur_iter, max_path, new_len = 0, 0, 0
    global_max = tiles
    prev_move = ""
    max_iter = 12
    # iterates a specific number of times to produce fastest results
    while cur_iter <= max_iter:
        # get all possible frontier states. If none break and return
        frontier_states = get_frontier_states_s(global_max, prev_move, width)
        if not frontier_states:
            break
        # choose frontier state with longest path to solution
        new_state, prev_move, new_path = best_state(frontier_states)
        # if new path is less than max_path found local max (break and return)
        if new_path < max_path:
            break
        # if new path is >= max path update variables and find solution length
        new_len = len(tiledriver.solve_puzzle(new_state))
        global_max = new_state
        # if new_len is greater than min_len, requirement satisfied
        if new_len >= min_len:
            break
        max_path = new_path
        cur_iter += 1
    return tuple(global_max), new_len


def shuffle_tiles(width: int, min_len: int,
                  solve_puzzle: Callable[[Tuple[int, ...]], str]
) -> Tuple[int, ...]:
    """
    Create a solvable shuffled puzzle of the given width with an optimal
    solution length equal to or greater than the given minimum length.

    >>> tiles = shuffle_tiles(3, 6, tiledriver.solve_puzzle)
    >>> len(tiledriver.solve_puzzle(tiles))
    6
    """
    cur_len = 0
    while cur_len < min_len:
        # generate a random set of tiles
        tiles = tuple(random_restart(width))
        # uphill climing to find tile orientation that meets min path length
        tiles, cur_len = uphill_climbing(tiles, min_len, width)
    return tiles


def main() -> None:
    pass # optional program test driver


if __name__ == "__main__":
    main()
