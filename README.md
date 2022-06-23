# python-shorties
Little 1 file python projects

## Sudoku Solver
Just trying out backtracking and comparing its performance to how I'd play.  Might look better performance-wise with less terminal output.
Might experiment with image recognition to read in puzzles much later.

## Kenken Solver
More backtracking, similar to sudoku but more complicated to implement the layout and rules.
Copied and modified from Sudoku almost no changes to the backtracking code, lots of unused leftovers to cleanout.  Doesn't read in puzzles any pleasant way.

## Menace Tic-Tac-Toe
Matchbox and beads based tic tac toe player.
&emsp;Requires matplotlib
python menace.py -q 2000
&emsp;Will play 2000 games X bot vs O bot and make 2 graphs
&emsp;-q suppresses printing every game result
Room for improvement
&emsp;Implement save / load the learned state
&emsp;Don't waste saving the symmetic board numbers
&emsp;Don't save separate X or O beads
&emsp;&emsp;Every other board set is X or O's turn only
&emsp;Refactor ugly large functions
&emsp;Optimize the symmetry tests?
