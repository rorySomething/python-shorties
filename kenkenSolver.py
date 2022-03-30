"""
Kenken Solver
    Copied from sudoku solver
    How do we feed in the board?
    Size and list of blocks with op result r,c r,c r,c ...

How many ways to solve?
1. Brute Force (Iterative?)
    Fill squares with every number combination and test for a valid solution.
2. Backtracking (Recursive?)
    Try every number in each square but step back to previous square once a square can't place a valid solution
3. Something Smart
    Program search based on game rules like a person would play
    Check columns, rows, blocks for placement options for each number until you need to guess, then mix in backtracking
4. ML Sorcery?
    Train a neural network to play?
    How would we input blocks and their math rules?
"""
    #TODO Clean out unused SudokuSolver junk
    #TODO Speed backtracking by ruling out numbers, e.g. If 10x, rule out 3, 4, and 6
    #Only need 1 pass to generate exclusions for blocks and pass that to the cells for lookup while backtracking

from math import isqrt
from time import perf_counter
from functools import reduce


"""OOP Monster"""
class Cell:
    def __init__(self, row = 0, col = 0, number = 0, maxVal = 6):
        self.number = number
        self.possible = [x for x in range(1, maxVal) if self.number == 0]
        self.block = None # Reference to block
        self.row = row
        self.col = col

class Block:
    def __init__(self, op = '', result = 0, cells = []):
        self.cells = cells # List not used outside
        self.result = result
        self.op = op

    def isValid(self):
        vals = [x.number for x in self.cells]
        print(vals)
        if 0 in vals:
            print('Has 0')
            return True
        else:
            return self.isSolved()

    def isSolved(self):
        vals = [x.number for x in self.cells]
        if self.op == '+':
            return sum(vals) == self.result
        elif self.op in ['*', 'x', '×']:
            prod = reduce(lambda x,y: x*y, vals)
            return prod == self.result
        # Max value first for - or ÷
        vals.sort(reverse=True)
        if self.op in ['/', '÷']:
            r = reduce(lambda x,y: x/y, vals)
            print('division', vals, r)
            return self.result == reduce(lambda x,y: x/y, vals)
        elif self.op == '-':
            r = reduce(lambda x,y: x-y, vals)
            print('subtraction', vals, r)
            return self.result == reduce(lambda x,y: x-y, vals)
        else:
            raise RuntimeError("Missing operation for a KenKen block")

class Board:
    """Kenken Board
    
    Just holds data and tests

    cells - list of Cells
    blocks - list of Blocks
    """
    def __init__(self, size = 0, blocks = []):
        """
        size is number of rows or columns
        blocks is a long list
          op, result, [cell indices], op, result, [cell indices], ...
        """
        self.size = size
        self.cells = [Cell(row = x//size, col = x%size, maxVal=size) for x in range(size**2)]
        self.blocks = []
        for i in range(0, len(blocks), 3):
            op = blocks[i]
            result = blocks[i+1]
            cells = [self.cells[j] for j in blocks[i+2]]
            self.blocks.append(Block(op, result, cells))
            b = self.blocks[-1]
            for c in b.cells:
                c.block = b

    def __str__(self):
        """Print pretty square

        .-----------------------.
        |Label  .   .   .   .   |
        | # . # . # . # . # . # |
        |                       |
        . is ' ' or '|'

        """
        # TODO Label blocks 120×, 2÷, etc.
        width = self.size * 4 + 1
        s = ""
        s += '.' + '-' * (width - 2) + '.\n'
        # TODO Refactor these rows into a list
        row0 = "|"
        row1 = "|"
        row2 = "|"
        row3 = "|"
        for i, c in enumerate(self.cells):
            col = i % self.size
            row = i // self.size
            row0 += '   '
            row1 += ' {} '.format(c.number)
            row2 += '   '
            down = None
            if row < self.size-1:
                down = self.cells[i+self.size]
                if c.block == down.block:
                    row3 += '   '
                else:
                    row3 += '---'
            # Handle right walls
            if col == self.size-1:
                row0 += "|\n"
                row1 += "|\n"
                row2 += "|\n"
                row3 += "|\n"
                s += row0 + row1 + row2
                if down is not None:
                    s += row3
                row0 = "|"
                row1 = "|"
                row2 = "|"
                row3 = "|"
            else:
                right = self.cells[i+1]
                if right.block == c.block:
                    row0 += ' '
                    row1 += ' '
                    row2 += ' '
                    row3 += '.'
                else:
                    row0 += '|'
                    row1 += '|'
                    row2 += '|'
                    row3 += '+'
        s += '\'' + '-' * (width - 2) + '\'\n'
        return s

    def getRow(self, index):
        start = index*self.size
        end = start + self.size
        return [self.cells[i].number for i in range(start, end)]

    def getRowPossible(self, index):
        start = index*self.size
        end = start + self.size
        return [self.cells[i].possible for i in range(start, end)]

    def getColumn(self, index):
        start = index
        end = self.size**2
        return [self.cells[i].number for i in range(start, end, self.size)]

    def getColumnPossible(self, index):
        start = index
        end = self.size**2
        return [self.cells[i].possible for i in range(start, end, self.size)]

    def getBlock(self, cellIndex):
        b = self.cells[cellIndex].block
        return [c.number for c in b.cells]

    def validNumberInRow(self, number, index):
        r = index//self.size
        return number not in self.getRow(r)
    
    def validNumberInColumn(self, number, index):
        c = index % self.size
        return number not in self.getColumn(c)

    def validNumberInBlock(self, number, cellIndex):
        cell = self.cells[cellIndex]
        # Probably overkill keeping number or not...
        original = cell.number
        cell.number = number
        good = cell.block.isValid()
        if good:
            return True
        else:
            cell.number = original
            return False

    def isValidNumber(self, num, index):
        return self.validNumberInRow(num, index) \
            and self.validNumberInColumn(num, index) \
            and self.validNumberInBlock(num, index)

    def backtrack(self, num, cellIndex):
        N = self.size
        r = cellIndex//N
        if r == N: # Done
            return True
        # Find next empty cell
        while self.cells[cellIndex].number != 0:
            cellIndex += 1
            r = cellIndex//N
            if r == N:
                return True # Every cell filled
        c = cellIndex % N
        for num in range(num, N+1):
            if not self.isValidNumber(num, cellIndex):
                continue
            print(num, 'at {}, {}'.format(r,c))
            self.cells[cellIndex].number = num
            print(self)
            if not self.backtrack(1, cellIndex + 1):
                continue
            else:
                return True
        self.cells[cellIndex].number = 0 # Backtrack
        return False

    def printPossible(self):
        """Print possible numbers

        9x9 grid of 3x3 grid single space gap

        123 12   2  | 123 123 123
        456 4 6  56
        789   9 789

        123

        Loops
          main rows 9x9 sudoku cells
          minor rows for possible 123, 456, 789 rows
          sudoku columns
          numbers in minor col based on minor row
        """
        s = ""
        sep1 = (' '*12 + '| ')*2 + ' '*11 + '\n'
        sep2 = sep1.replace(' ', '-').replace('|', '+')
        for i, row in enumerate(self.possible):
            if (i != 0) and (i%3 == 0):
                s += sep2
            for j in range(3): # 1 4 7
                for k, n in enumerate(row):
                    if (k != 0) and (k%3 == 0):
                        s += '| '
                    x = [x for x in range((j*3)+1, (j*3)+4)]
                    for l in x:
                        if l in n:
                            s += str(l)
                        else:
                            s += ' '
                    s += ' '
                s += '|\n'
            s += sep1
        print(s)

    def printPossibleBlock(self, x, y, sudokuGrid = 9):
        """

        Indices
        1 2 3 \n
        4 5 6 \n
        7 8 9

        For each index row
        123 123 123 \n
        """
        indices = self.getBlockIndices(x, y)
        #print(indices, len(indices))
        # Indices are row by row
        blockSize = isqrt(sudokuGrid)
        #print("size", blockSize)
        s = ""
        for row in range(blockSize): # 0, 3, 6
            rIndex = row * blockSize
            for j in range(blockSize): # minirow/col
                for col in range(blockSize): # 1 2 3 /n
                    index = rIndex + col
                    #print("Index", index)
                    #print("\t", indices[index])
                    r,c = indices[index]
                    p = self.possible[r][c]
                    x = [x for x in range((j*3)+1, (j*3)+4)]
                    for l in x:
                        if l in p:
                            s += str(l)
                        else:
                            s += ' '
                    s += ' '
                s += '\n'
            s += '\n'
        print(s)


    def updatePossible(self):
        """Remove set on board numbers from possible lists

        Returns number of changed cells"""
        changes = 0
        for i in range(81):
            r = i // 9
            c = i % 9
            n = self.numbers[r][c]
            if n == 0:
                continue
            # Clear row
            for j in self.possible[r]:
                if len(j) == 1:
                    continue
                if n in j:
                    j.remove(n)
                    changes += 1
            # Clear column
            for row in self.possible:
                if len(row[c]) == 1:
                    continue
                if n in row[c]:
                    row[c].remove(n)
                    changes += 1
                    row0 += ' '
                    row1 += ' '
                    row2 += ' '
                    row3 += '.'
            # Clear block
            r0 = r - r%3
            c0 = c - c%3
            for row in range(r0, r0+3):
                for col in range(c0, c0+3):
                    cell = self.possible[row][col]
                    if len(cell) > 1 and n in cell:
                        cell.remove(n)
                        changes += 1
        return changes

    def trySetBoard(self):
        """Look for possible numbers lists with only 1 option

        Return number of changes"""
        changes = 0
        for r in range(9):
            for c in range(9):
                p = self.possible[r][c]
                n = self.numbers[r][c]
                if not p and n == 0:
                    raise RuntimeError("The programmer is an idiot, let him know he messed up.")
                elif len(p) == 1 and n == 0:
                    self.numbers[r][c] = p.pop()
                    changes += 1
                elif len(p) == 1 and n != 0:
                    if n == p[0]:
                        p.pop()
                    else:
                        print("Problem at {} {}".format(r, c))
                else:
                    pass # many possible, hopefully n is 0...
        return changes

    def removeFromRow(self, num, rowIndex, exclude = []):
        changes = 0
        for i,c in enumerate(self.possible[rowIndex]):
            if i in exclude:
                continue
            if num in c:
                c.remove(num)
                changes += 1
        return changes

    def removeFromCol(self, num, colIndex, exclude = []):
        changes = 0
        for i,r in enumerate([row[colIndex] for row in self.possible]):
            if i in exclude:
                continue
            # r is list so this is a reference
            if num in r:
                r.remove(num)
                changes += 1
        return changes

    def getBlockIndicesForCell(self, row, col, sudokuGrid = 9):
        """Return list of (row, col) indices for a block

        Give a cell and return the block it belongs to
        by calling getBlockIndices
        """
        blockX = (row // sudokuGrid) + 1 # 0 to 8 -> 0 + 1
        blockY = (col // sudokuGrid) + 1
        return self.getBlockIndices(blockX, blockY, sudokuGrid)

    def getBlockIndicesFlat(self, blockX, blockY, sudokuGrid = 9):
        """Return list of indices in a sudoku block.

        block X,Y indices start from 0
        Max grid X,Y is sqrt(sudokuGrid) - 1
        For 9x9 sudoku, flat indexing is 0-80 in list of sudoku board
        e.g. Block 0,0 should return [0, 1, 2, 9, 10, 11, 18, 19, 20]
             0  1  2
             9 10 11
            18 19 20
        """
        blockSize = isqrt(sudokuGrid) # TODO Check for bad grid
        indices = []
        row0 = blockX * blockSize # 0, 1, 2 -> 0, 3, 6
        col0 = blockY * blockSize
        for row in range(row0, row0 + blockSize):
            for col in range(col0, col0 + blockSize):
                indices.append(row * sudokuGrid + col)
        return indices

    def removeFromBlock(self, num, blockX, blockY, exclude = []): # TODO Add sudokuGrid parameter everywhere?
        """

        NOTE: Expect exclude as tuples (row, col)
        """
        changes = 0
        indices = self.getBlockIndices(blockX, blockY)
        for c in indices:
            if c in exclude:
                continue
            row, col = c
            cell = self.possible[row][col]
            if num in cell:
                print(self.possible[row][col])
                cell.remove(num)
                changes += 1
                print(self.possible[row][col])
        return changes

    def playerSolver(self):
        return NotImplementedError()
        """Try to solve sudoku like a player would.

        Check rows, columns, and blocks to find/rule out number placement.
        Use backtracking when we need to guess."""
        currNumber = 1
        flatBoard = [n for row in self.numbers for n in row]
        self.updatePossible()
        cycles = 0
        changed = True
        while changed:
            print(self)
            changed = False
            self.printPossible()
            changes = self.updatePossible()
            changes += self.trimPairsAndTriplets()
            changes += self.trySetBoard()
            changed = changes > 0
            cycles += 1
            print("{} cycles".format(cycles), end='\r')
        print("")

def run():
    testBoard = [
        '*', 120, [0,1,6,7],
        '+', 11, [2,8,9],
        '-', 1, [3,4],
        '/', 2, [5,11],
        '*', 6, [10,16],
        '/', 2, [12,18],
        '/', 3, [13,14],
        '*', 20, [15,20,21],
        '+', 18, [17,23,29,35],
        '*', 16, [19,25,26],
        '+', 13, [22,27,28],
        '-', 3, [24,30],
        '-', 3, [31,32],
        '-', 2, [33,34],
            ]
    p0 = perf_counter()
    b = Board(6, testBoard)
    print(b)
    b.backtrack(1, 0)
    print(b)
    pT = perf_counter() - p0
    print("Backtrack", pT)



if __name__ == "__main__":
    print("Howdy.")
    run()

