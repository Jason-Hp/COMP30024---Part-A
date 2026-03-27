# COMP30024 Artificial Intelligence, Semester 1 2026
# Project Part A: Single Player Cascade

from collections import deque

from .core import BOARD_N, CellState, Coord, Direction, Action, MoveAction, EatAction, CascadeAction, PlayerColor
from .utils import render_board

# For convenience (stores its values instead of enum objects)
RED = PlayerColor.RED.value
BLUE = PlayerColor.BLUE.value

# Each board state is represented as an entry where it's (row, col, color_value, height)
State = tuple[tuple[int, int, int, int], ...]
# Internal stack representation (color, height)  
Stack = tuple[int, int]
# Initial start state (state has no parent)
_PARENT_NONE = (-1, None)

# Checks whether a coordinate is on the board
def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < BOARD_N and 0 <= c < BOARD_N

# Converets assignment input into the internal immutable State
def state_from_board(board: dict[Coord, CellState]) -> State:
    return tuple(
         # sorted so that two identical boards always get represented by the exact same tuple
        sorted((coord.r, coord.c, cell.color.value, cell.height) for coord, cell in board.items())
    )
    
# Converts the immutable tuple state into a mutable dictionary
def board_from_state(state: State) -> dict[tuple[int, int], Stack]:
    return {(r, c): (color, height) for r, c, color, height in state}

# Converts the temporary mutable internal board back into immutable tuple
def state_from_internal(board: dict[tuple[int, int], Stack]) -> State:
    return tuple(
        sorted(
            (r, c, stack[0], stack[1]) 
            for (r, c), stack in board.items()
            if in_bounds(r, c) # Extra guard
        )
    )
    
# Checks if there's no blues left
def reaches_goal(state: State) -> bool:
    return all(color != BLUE for _, _, color, _ in state)

# Checks if there's still reds on the board
def has_red(state: State) -> bool:
    return any(color == RED for _, _, color, _ in state)

# Simulates a possible MOVE
def move(state: State, r: int, c: int, direction: Direction) -> State | None:
    """
    1. Convert state into internal mutable board
    2. Find the source stack
    3. Confirm source exists and is RED
    4. Compute destination
    5. Reject if destination is not on board
    6. Inspect what is on the destination board (empty, blue, red)
    """
    
    board = board_from_state(state)
    source = (r, c)
    stack = board.get(source)
    if stack is None or stack[0] != RED:
        return None
    
    dest = (r + direction.r, c + direction.c)
    if not in_bounds(*dest):
        return None
    
    target = board.get(dest)
    if target is None:
        del board[source]
        board[dest] = stack
        return state_from_internal(board)
    
    if target[0] != RED:
        return None
    
    del board[source]
    board[dest] = (RED, stack[1] + target[1])
    return state_from_internal(board)

# Simulates a possible EAT
def eat(state: State, r: int, c: int, direction: Direction) -> State | None:
    """
    1. Convert State into internal mutable board
    2. Make sure the source exists and is a RED stack
    3. Compute the adjacent destination square
    4. Reject if not on board
    5. Reject if destination is empty
    6. Reject if Destination is not BLUE
    7. Reject if Red's height is less than Blue's height
    """
    
    board = board_from_state(state)
    source = (r, c)
    stack = board.get(source)
    if stack is None or stack[0] != RED:
        return None
    
    dest = (r + direction.r, c + direction.c)
    if not in_bounds(*dest):
        return None
    
    target = board.get(dest)
    if target is None or target[0] != BLUE:
        return None
    if stack[1] < target[1]:
        return None;
    
    del board[source]
    board[dest] = stack
    return state_from_internal(board)
    

# Helper function for cascade 
def push(board: dict[tuple[int, int], Stack], pos: tuple[int, int], direction: Direction):
    """
    Push the entire stack at pos one cell in direction, recursively pushing blockers in same direction.
    1. Removes the stack currently at pos
    2. Computes the next position one cell further in direction
    3. If that new position is not on the board, the stack is lost
    4. If that new position is occupied, recursively push the blocker first
    5. Place the original stack in the now free next position
    """
    
    stack = board.pop(pos)
    next_row = pos[0] + direction.r
    next_col = pos[1] + direction.c
    
    if not in_bounds(next_row, next_col):
        return
    
    next = (next_row, next_col)
    if next in board:
        push(board, next, direction)
    board[next] = stack

# Simulates a possible CASCADE
def cascade(state: State, r: int, c: int, direction: Direction) -> State | None:
    """
    1. Convert state into internal mutable board
    2. Validates action (stack is red and height >= 2)
    3. Removes original stack from board
    4. Spreads one token at a time
    """
    
    board = board_from_state(state)
    source = (r, c)
    stack = board.get(source)
    if stack is None or stack[0] != RED or stack[1] < 2:
        return None
    
    del board[source]
    
    for step in range(1, stack[1] + 1):
        next_row = r + direction.r * step
        next_col = c + direction.c * step
        if not in_bounds(next_row, next_col):
            continue
        
        pos = (next_row, next_col)
        if pos in board:
            push(board, pos, direction)
        board[pos] = (RED, 1)
        
    return state_from_internal(board)

# Determines legally, what can RED do on the current board
def generate_successors(state: State) -> list[tuple[Action, State]]:
    """
    1. Creates a list for all successors, storing action object to return later and the resulting next state
    2. Loops through every stack in the state
    3. For each red stack, try every direction
        If Direction is legal, it adds the action to the list
    """
    
    successors: list[tuple[Action, State]] = []
    
    for r, c, color, _ in state:
        if color != RED:
            continue
        
        coord = Coord(r, c)
        directions = (
            Direction.Up,
            Direction.Down,
            Direction.Left,
            Direction.Right,
        )
        for direction in directions:
            moved = move(state, r, c, direction)
            if moved is not None:
                successors.append((MoveAction(coord, direction), moved))
                
            eaten = eat(state, r, c, direction)
            if eaten is not None:
                successors.append((EatAction(coord, direction), eaten))
                
            cascaded = cascade(state, r, c, direction)
            if cascaded is not None:
                successors.append((CascadeAction(coord, direction), cascaded))
             
    # Sorting not necessary, just makes order deterministic    
    successors.sort(key=lambda item: str(item[0])) 
    return successors

# Reconstructing the final action sequence
def reconstruct_path(goal: State, parent: dict[State, tuple[State | int, Action | None]]) -> list[Action]:
    """
    1. Starts from goal state
    2. Look up parent and action done
    3. Add action to path
    4. Repeat until reached start state
    5. Reverse the path
    """
    
    path: list[Action] = []
    state = goal
    while True:
        prev_state, action = parent[state]
        if action is None:
            break
        path.append(action)
        state = prev_state
    path.reverse()
    return path
    
# Search best way to defeat BLUE using BFS
def search(
    board: dict[Coord, CellState]
) -> list[Action] | None:
    """
    Return an optimal minimal-action solution using BFS(breadth-first search).
    Since every legal action has unit cost of 1, BFS explores states in nondecreasing
    solution cost and the first goal found is optimal.

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
    
    # REMEMBER TO REMOVE BEFORE FINAL SUBMISSION!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    print(render_board(board, ansi=True))

    # Convert input into immutable tuple 
    start = state_from_board(board)
    
    # Early exits (no blue or no red)
    if reaches_goal(start):
        return []
    if not has_red(start):
        return None
    
    # FIFO order 
    frontier: deque[State] = deque([start])
    # Used to check visited states and for path reconstruction
    parent: dict[State, tuple[State | int, Action | None]] = {start: _PARENT_NONE}
    
    while frontier:
        # Removes oldest state from queue
        state = frontier.popleft()
        
        # Expand successors
        for action, next_state in generate_successors(state):
            if next_state in parent:
                continue
            
            # Record how it got to the state
            parent[next_state] = (state, action)
            
            if reaches_goal(next_state):
                return reconstruct_path(next_state, parent)
            
            # Queue for later expansion
            frontier.append(next_state)
    
    # No solution exists    
    return None
    
