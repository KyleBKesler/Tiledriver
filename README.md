# Tiledriver

Project for CSC 480 (Aritificial Intelligence) Writing an AI solve the sliding tile puzzle using the A* Search algorithm.

![My Image](ex_puzzle.jpg "Example TilePuzzle")

In this project I defined 2 main classes:

TilePuzzle - defines the size and starting state of the tile puzzle
State

TilePuzzle defines the sliding puzzle game. It will allow you to set the size of the puzzle (nxn), as well as let you provide an initial state for the puzzle in which you want to solve. If no initial state is given, it will generate a random puzzle of a user defined size.

state: What the current arrangement of tiles is
puzzle: a TilePuzzle object
Previous: What the previous node was
path_from_start: The current set of moves that have been taken to get the from the initial node to this node
g: the number of moves made from the start
h: a Heuristic which provides an approximation this node is from the goal state.
f: g + h
Tiledriver

Tiledriver uses StateNodes to utilize the A* Search in order to find the optimal number of moves to the goal state. It requires an the initial state of a puzzle, and then finds the optimal path to solve it by searching StateNodes with lowest f value.

**The Heuristic class was given to me by my professor, but the rest was written exclusively by me.**
