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

    for k, v in board.items():
        if v.color == PlayerColor.BLUE:
            max_blue_height = max(max_blue_height, v.height)
            number_of_blues += 1
        else:
            total_red_height += v.height
        

    queue = deque()
    
    # Edge case
    if (total_red_height < max_blue_height):
        return None
    
    queue.append(Node(board.copy(), [], number_of_blues))

    # BFS WITH SAME/UNIFORM COST EDGES MEANS GENERATION RESULTS IN OPTIMALITY HERE, NO NEED TO WAIT UNTIL EXPANDED
    
    # FOR TMR, basically do bfs with nodes in queue, until the generated node contains remaining_blues = 0
    # during EXPANSION of a node, ofc do the movement (all of the 12), for each, generate a new node for the frontier, with new state, path, and remaining_blues ofc


    visited_set = set()
    visited_set.add(frozenset(board.items()))
    directions = [Direction.Down, Direction.Left, Direction.Right, Direction.Up]
    while queue:
        # Expand a node AKA remove from queue/Frontier
        expanded_node = queue.popleft()
        current_state = expanded_node.state.copy()

        for k, v in current_state.items():
            if v.color is not PlayerColor.RED:
                continue

            current_cell_state = v
            expanded_node.state.pop(k)

            # This is optimizaton to somewhat reduce branching factor from 12 -> 8~ 
            eat_list = []

            # Move and cascade first
            for direction in directions:
                generated_node = move(expanded_node, direction, eat_list, current_cell_state, k)

                if generated_node:
                    state_set = frozenset(generated_node.state.items())
                    if state_set not in visited_set:
                        visited_set.add(state_set)
                        queue.append(generated_node)
                        
                        # Might be unecessary btw
                        if generated_node.remaining_blues == 0:
                            return generated_node.path

                # make sure height >= 2
                if current_cell_state.height >= 2:
                    generated_node = cascade(expanded_node, direction, current_cell_state, k)
                
                    if generated_node:
                        state_set = frozenset(generated_node.state.items())
                        if state_set not in visited_set:
                            visited_set.add(state_set)
                            queue.append(generated_node)
                            if generated_node.remaining_blues == 0:
                                return generated_node.path
            
            # eat from eat list
            for eat_coord in eat_list:
                generated_node = eat(expanded_node, eat_coord, current_cell_state, k)
                if generated_node:
                    state_set = frozenset(generated_node.state.items())
                    if state_set not in visited_set:
                        visited_set.add(state_set)
                        queue.append(generated_node)
                        if generated_node.remaining_blues == 0:
                            return generated_node.path
            
            # backtrack
            expanded_node.state[k] = v


# Util functions/classes below

# Node for graph
class Node:

    def __init__(self, state, path, remaining_blues):
        self.state = state
        self.path = path
        self.remaining_blues = remaining_blues

    # state is basically current board state
    state: dict[Coord, CellState]

    path: list[Action]

    # FASTER GOAL CHECK
    remaining_blues = 0

def move(node: Node, direction: Direction, eat_list: list, current_cell_state: CellState, current_coord: Coord):
    coord = current_coord
    try:
        coord = Coord(coord.r + direction.__getattribute__("r"), coord.c + direction.__getattribute__("c"))
    except:
        return None


    if node.state.get(coord):
        cellstate = node.state[coord]
        if cellstate.color == PlayerColor.BLUE:
            eat_list.append([coord, direction])
            return None
        else:
            # cellstate is red
            state = node.state.copy()
            path = node.path.copy()

            state[coord] = CellState(PlayerColor.RED, cellstate.height + current_cell_state.height)

            path.append(MoveAction(current_coord, direction))
            return Node(state, path, node.remaining_blues)
    else:
        state = node.state.copy()
        path = node.path.copy()
        state[coord] = CellState(PlayerColor.RED, current_cell_state.height)
        path.append(MoveAction(current_coord, direction))
        return Node(state, path, node.remaining_blues)


def eat(node: Node, coord_and_dir: list, current_cell_state: CellState, current_coord: Coord):
    coord = coord_and_dir[0]
    dir = coord_and_dir[1]

    blue_cell = node.state[coord]
    if (current_cell_state.height < blue_cell.height):
        return None

    # If able to eat
    state = node.state.copy()
    path = node.path.copy()
    state[coord] = CellState(PlayerColor.RED, current_cell_state.height)
    path.append(EatAction(current_coord, dir))
    return Node(state, path, node.remaining_blues - 1)

def cascade(node: Node, direction: Direction, current_cell_state: CellState, current_coord: Coord):
    
    # Cascade out of bounds
    coord = current_coord
    try:
        coord = Coord(coord.r + direction.__getattribute__("r"), coord.c + direction.__getattribute__("c"))
    except:
        return None

    state = node.state.copy()
    path = node.path.copy()
    remaining_blues = node.remaining_blues
    path.append(CascadeAction(current_coord, direction))

    current_height = current_cell_state.height

    #reset coord var
    coord = current_coord

    # Cascade height no of times
    for _ in range(current_height): 
        
        try:
            coord = Coord(coord.r + direction.__getattribute__("r"), coord.c + direction.__getattribute__("c"))
        except:
            break
        
        next_coord = coord
        prev_state_cell = None
        pushed_out = False
        while(state.get(next_coord)):
            cell_state = state[next_coord]
            if prev_state_cell is None:
                state.pop(next_coord, None)
            else:
                state[next_coord] = prev_state_cell
            try:
                next_coord = Coord(next_coord.r + direction.__getattribute__("r"), next_coord.c + direction.__getattribute__("c"))
                prev_state_cell = cell_state
            except:
                pushed_out = True
                if cell_state.color == PlayerColor.BLUE:
                    remaining_blues -= 1
                break
        
        if not pushed_out:
            state[next_coord] = prev_state_cell

        state[coord] = CellState(PlayerColor.RED, 1)
    
    return Node(state, path, remaining_blues)
