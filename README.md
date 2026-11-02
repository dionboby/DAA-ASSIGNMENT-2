# Campus Route Finder (Floyd-Warshall)

24CCT301 Design and Analysis of Algorithms, Assignment 2: GUI-Based Algorithm Implementation

A Python desktop app that finds the shortest walking distance between every pair of campus buildings using the Floyd-Warshall algorithm. It also suggests the best building for a help desk: the one with the least total walking distance to all other buildings.

## Requirements

- Python 3.8 or newer
- Tkinter (included with the standard Windows and macOS installers; on Linux run `sudo apt install python3-tk`)
- No other libraries needed

## How to run

**In VS Code**

1. Open the folder containing `campus_route_finder.py` (File > Open Folder).
2. Open `campus_route_finder.py`.
3. Click the **Run** (play) button at the top right.

**In a terminal**

```
python campus_route_finder.py
```

If `python` is not recognised, use `py campus_route_finder.py`.

## How to use

1. Type paths in the box, one per line: `Building1 Building2 Distance` (metres). Use one word per building. Or pick a test case from the dropdown.
2. Tick **Paths are two-way** for normal roads, or untick it for one-way paths.
3. Press **Build**.
4. Press **Step** to process one pivot building at a time, **Back** to go one step back, **Run all** to jump to the final result, **Reset** to start again.
5. Under **Find a route**, choose two buildings and press **Show route**. The shortest route is drawn in red on the map.
6. At the final step, the best help desk location and a ranking of all buildings appear at the bottom right.

What the display shows:

- Orange circle on the map: the current pivot building.
- Orange cells in the matrix: the pivot row and column.
- Green cells: distances that improved in this step.
- The step log lists every improvement, for example `Gate -> Canteen: ∞ -> 280`.

## Built-in test cases

| Test case | What it checks |
|---|---|
| Campus paths (sample) | Normal case with 9 buildings |
| Boundary: single path | Smallest valid input |
| Boundary: disconnected buildings | Unreachable pairs stay at ∞ |
| One-way paths | Non-symmetric distances |
| Boundary: negative cycle | Detected and reported |
| Boundary: empty input | Error message |
| Boundary: invalid distance | Error message with line number |

## Algorithm and complexity

Floyd-Warshall is a dynamic programming algorithm. For each pivot building `k`, it checks every pair `(i, j)` and updates the distance if going through `k` is shorter:

```
D[i][j] = min(D[i][j], D[i][k] + D[k][j])
```

- Time: Θ(V³) in the best, average and worst case
- Space: Θ(V²) for the distance and next-hop matrices
- A negative value on the diagonal means a negative cycle exists
- Input is limited to 12 buildings

## Files

| File | Purpose |
|---|---|
| `campus_route_finder.py` | Source code (algorithm and GUI) |
| `Campus_Route_Finder_Report.docx` | Project report |
| `README.md` | This file |
