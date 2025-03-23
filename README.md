# Maze Solver Visualizer

This project is an interactive maze solver application developed using Python and Pygame. It allows you to visualize and compare different maze generation and solving algorithms.

## Features

- **Maze Generation**: Create random mazes using two different algorithms:
  - Recursive Backtracking
  - Prim's Algorithm

- **Maze Solving**: Solve mazes with seven different algorithms:
  - Wall Follower
  - Dijkstra's Algorithm
  - Dead End Filling
  - BFS (Breadth-First Search)
  - DFS (Depth-First Search)
  - IDS (Iterative Deepening Search)
  - A* (A Star)

- **Algorithm Comparison**: Compare between two and four algorithms side by side to observe their performance and efficiency.

- **Visualization**: All algorithms are visualized step by step:
  - Green: Starting point
  - Red: End point
  - Dark Red: Visited cells
  - Yellow: Solution path
  - Red Circle: Current cell being processed

## Requirements

- Python 3.6 or higher
- pygame
- numpy

## Installation

1. Clone or download the project
2. Install the required packages:

```
pip install -r requirements.txt
```

## Usage

To start the program:

```
python main.py
```

### Main Menu

From the main menu, you can:

1. **Generate Maze**: Select an algorithm and adjust the size to create a new maze.
2. **Solve Maze**: Select an algorithm to solve the current maze.
3. **Compare Algorithms**: Select 2-4 algorithms to compare them side by side.
4. **Exit**: Close the program.

### Controls

- **ESC**: Return to the main menu
- **SPACE**: Pause/resume algorithm execution (in solving and comparison modes)

## Project Structure

- `main.py`: Main program file
- `maze.py`: Maze class and generation algorithms
- `algorithms.py`: Maze solving algorithms
- `ui.py`: User interface components

## About the Algorithms

### Maze Generation

- **Recursive Backtracking**: An algorithm that uses depth-first search. It creates the maze by moving in random directions and backtracking when it reaches a dead end.
- **Prim's Algorithm**: A minimum spanning tree algorithm. It starts from a random cell and creates the maze by adding frontier cells.

### Maze Solving

- **Wall Follower**: Follows walls using the right (or left) hand rule. It doesn't work for all mazes, only for "simply connected" mazes.
- **Dijkstra**: Evaluates all possible paths to find the shortest path. Guarantees the shortest path.
- **Dead End Filling**: Aims to find the main path by filling in dead ends. Effective in simple mazes.
- **BFS**: Breadth-first search expands all paths equally to find the shortest path.
- **DFS**: Depth-first search follows a path to the end, backtracking if it reaches a dead end.
- **IDS**: Applies depth-limited DFS with increasing depths. Finds the shortest path like BFS but uses less memory.
- **A***: Enhances Dijkstra's algorithm by using a heuristic (estimated distance to the goal). Usually faster than Dijkstra. 