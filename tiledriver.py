# Name: Kyle Kesler
# Course: CSC 480
# Instructor: Daniel Kauffman
# Assignment: Tile Driver
# Term: Spring 2021


import queue
from typing import List, Tuple, Set


class Heuristic:

    @staticmethod
    def get(tiles: Tuple[int, ...]) -> int:
        """
        Return the estimated distance to the goal using Manhattan distance
        and linear conflicts.

        Only this static method should be called during a search; all other
        methods in this class should be considered private.

        >>> Heuristic.get((0, 1, 2, 3))
        0
        >>> Heuristic.get((3, 2, 1, 0))
        6
        """
        width = int(len(tiles) ** 0.5)
        return (Heuristic._get_manhattan_distance(tiles, width)
                + Heuristic._get_linear_conflicts(tiles, width))

    @staticmethod
    def _get_manhattan_distance(tiles: Tuple[int, ...], width: int) -> int:
        """
        Return the Manhattan distance of the given tiles, which represents
        how many moves is tile is away from its goal position.
        """
        distance = 0
        for i in range(len(tiles)):
            if tiles[i] != 0:
                row_dist = abs(i // width - tiles[i] // width)
                col_dist = abs(i % width - tiles[i] % width)
                distance += row_dist + col_dist
        return distance


    @staticmethod
    def _get_linear_conflicts(tiles: Tuple[int, ...], width: int) -> int:
        """
        Return the number of linear conflicts in the tiles, which represents
        the minimum number of tiles in each row and column that must leave and
        re-enter that row or column in order for the puzzle to be solved.
        """
        conflicts = 0
        rows = [[] for i in range(width)]
        cols = [[] for i in range(width)]
        for i in range(len(tiles)):
            if tiles[i] != 0:
                if i // width == tiles[i] // width:
                    rows[i // width].append(tiles[i])
                if i % width == tiles[i] % width:
                    cols[i % width].append(tiles[i])
        for i in range(width):
            conflicts += Heuristic._count_conflicts(rows[i])
            conflicts += Heuristic._count_conflicts(cols[i])
        return conflicts * 2

    @staticmethod
    def _count_conflicts(ints: List[int]) -> int:
        """
        Return the minimum number of tiles that must be removed from the given
        list in order for the list to be sorted.
        """
        if Heuristic._is_sorted(ints):
            return 0
        lowest = None
        for i in range(len(ints)):
            conflicts = Heuristic._count_conflicts(ints[:i] + ints[i + 1:])
            if lowest is None or conflicts < lowest:
                lowest = conflicts
        return 1 + lowest

    @staticmethod
    def _is_sorted(ints: List[int]) -> bool:
        """Return True if the given list is sorted and False otherwise."""
        for i in range(len(ints) - 1):
            if ints[i] > ints[i + 1]:
                return False
        return True


class TilePuzzle:
    def __init__(self, tiles: Tuple[int, ...], size: int, path: str):
        self.width = int(size**0.5)
        self.start_state = State(tiles, path)
        self.frontier = queue.PriorityQueue()


class State:
    def __init__(self, tiles: Tuple[int, ...], path: str):
        self.tiles = tiles
        self.path = path
        self.h = Heuristic.get(tiles)
        self.f = len(self.path) + self.h

    def __lt__(self, other):
        """Method so that State objects may be compared for priority"""
        return self.f < other.f


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


def get_possible_moves(prev_move: str) -> str:
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
    dist = int(move_sizes.get(move))
    # swapping the blank tile (0) with the tile in the position to be moved to
    zero_loc = tiles.index(0)
    replace_tile = tiles[zero_loc + dist]
    tiles[zero_loc + dist] = 0
    tiles[zero_loc] = replace_tile
    return tiles


def create_new_states(puzzle: TilePuzzle, state: State, prev_move: str,
                                        explored: Set[tuple]) -> None:
    """
    Using the previous move, determines possible moves that are valid and
    non-opposing to create frontier states. Adds frontier states that have not
    been explored yet to the priority queue.
    """
    if state.path != "":
        prev_move = state.path[-1]
    # obtain list of possible non-opposing moves
    possible_moves = get_possible_moves(prev_move)
    for i in possible_moves:
        # determine if move is valid (would it move blank tile off puzzle)
        if is_valid_move(state.tiles, i, puzzle.width):
            # swap the blank tile with tile in move direction
            moved = tuple(move_tile(list(state.tiles), i, puzzle.width))
            # create State object and add to priority queue if not explored
            if not moved in explored:
                new_st = State(moved, str(state.path + i))
                puzzle.frontier.put(new_st)


def solve_puzzle(tiles: Tuple[int, ...]) -> str:
    """
    Return a string (containing characters "H", "J", "K", "L") representing the
    optimal number of moves to solve the given puzzle.
    """
    # create set to hold explored states (set has O(1) membership testing)
    explored = set() # type: Set[tuple]
    # create initial TilePuzzle object
    puzzle = TilePuzzle(tiles, len(tiles), "")
    if puzzle.start_state.f == 0:
        return ''
    # add first set of frontier states to priority queue
    create_new_states(puzzle, puzzle.start_state, "", explored)
    next_state = puzzle.frontier.get()
    # when the path to goal is 0 puzzle has been solved
    while next_state.h != 0:
        # add tile arrangment to explored set
        explored.add(next_state.tiles)
        create_new_states(puzzle, next_state, next_state.path, explored)
        # get the next state with lowest past cost from priority queue
        next_state = puzzle.frontier.get()
    return next_state.path


def main() -> None:
    """Test puzzle driver"""
    puzzle = (0, 3, 6, 5, 4, 7, 2, 1, 8)
    optimal_path = solve_puzzle(puzzle)
    print(optimal_path)


if __name__ == "__main__":
    main()
