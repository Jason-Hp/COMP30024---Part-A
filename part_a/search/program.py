# COMP30024 Artificial Intelligence, Semester 1 2026
# Project Part A: Single Player Cascade

from .core import CellState, Coord, Direction, Action, MoveAction, EatAction, CascadeAction, PlayerColor
from .utils import render_board
from collections import deque

def search(
    board: dict[Coord, CellState]
) -> list[Action] | None:
    """
    This is the entry point for your submission. You should modify this
    function to solve the search problem discussed in the Part A specification.
    See `core.py` for information on the types being used here.

    Parameters:
        `board`: a dictionary representing the initial board state, mapping
            coordinates to `CellState` instances (each with a `.color` and
            `.height` attribute).

    Returns:
        A list of actions (MoveAction, EatAction, or CascadeAction), or `None`
        if no solution is possible.
    """

    # The render_board() function is handy for debugging. It will print out a
    # board state in a human-readable format. If your terminal supports ANSI
    # codes, set the `ansi` flag to True to print a colour-coded version!
    print(render_board(board, ansi=True))

    # Do some impressive AI stuff here to find the solution...
    # ...
    # ... (your solution goes here!)
    # ...

    #Find MAX blue height
    #Get Blue Count
    #Find Sum of all red height
    #Compare and return None if less
    max_blue_height = 0
    number_of_blues = 0
    total_red_height = 0
    starting_nodes = []
    for k, v in board.items():
        if v.color == PlayerColor.BLUE:
            max_blue_height = max(max_blue_height, v.height)
            number_of_blues += 1
        else:
            total_red_height += v.height
            node = Node(board.copy(), k, 0)
            starting_nodes.append(node)
        
    for node in starting_nodes:
        node.remaining_blues = number_of_blues

    
    # Edge case
    if (total_red_height < max_blue_height):
        return None

    queue = deque()
    



    # Here we're returning "hardcoded" actions as an example of the expected
    # output format. Of course, you should instead return the result of your
    # search algorithm. Remember: if no solution is possible for a given input,
    # return `None` instead of a list.
    return [
        MoveAction(Coord(3, 3), Direction.Down),
        EatAction(Coord(4, 3), Direction.Down),
    ]

# Util functions/classes below


# Node for graph
class Node:

    # state is basically current board state
    state: dict[Coord, CellState]

    # red stack chosen (ADD this during GENERATION, USE this during EXPANSION)
    chosen: Coord

    # FASTER GOAL CHECK
    remaining_blues = 0