"""
Sudoku Solver

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
    81 input neurons a few hidden layers 81 output neurons
    Signals 0-9 input and 1-9 output... hopefully
"""

from math import isqrt
from time import perf_counter


"""OOP Monster"""
class Cell:
    def __init__(self, number = 0, fixed = False):
        self.number = number
        self.possible = [x for x in range(1, 10) if self.number == 0]
        self.fixed = fixed
    def isSet(self):
        return self.fixed or (self.number != 0)

class Block:
    def __init__(self, cells = []):
        self.cells = cells[:]
        while len(self.cells) < 9:
            self.cells.append(Cell(0))

class Board:
    """ Sudoku Board
    Handles everything...

    numbers - list of lists holding numbers in each row & col
    possible - lists 3 deep holding all numbers that could be in a cell or empty if it's a given number"""
    def __init__(self, numbers = []):
        self.numbers = [row[:] for row in numbers]
        self.possible = []
        for row in self.numbers:
            self.possible.append([])
            for n in row:
                if n == 0:
                    self.possible[-1].append([x for x in range(1, 10)])
                else: # Empty list
                    self.possible[-1].append([])
        self.stack = []

    def __str__(self):
        """Print pretty square
        2*9 + 3 spaces + 4 edges
        '| # # # '*3 + last |"""
        width = 2*9 + 7
        s = ""
        s += '.' + '-' * (width - 2) + '.\n'
        sep = '|' + '-------+'*2 + '-------|\n'
        for i, row in enumerate(self.numbers):
            if (i != 0) and (i%3 == 0):
                s += sep
            for j, n in enumerate(row):
                if j%3 == 0:
                    s += '| '
                s += '{0} '.format(n)
            s += '|\n'
        s += '\'' + '-' * (width - 2) + '\'\n'
        return s

    def getRow(self, index):
        return self.numbers[index]

    def getRowPossible(self, index):
        return self.possible[index]

    def getColumn(self, index):
        return [x[index] for x in self.numbers]

    def getColumnPossible(self, index):
        return [x[index] for x in self.possible]

    def getBlock(self, x, y):
        """Return 3x3 grid x, y from 0 to 2"""
        block = []
        for rows in range(y*3, y*3+3):
            for col in range(x*3, x*3+3):
                block.append(self.numbers[rows][col])
        return block

    def getBlockPossible(self, x, y):
        """Return 3x3 grid x, y from 0 to 2"""
        block = []
        for rows in range(y*3, y*3+3):
            block.append([])
            for col in range(x*3, x*3+3):
                block[-1].append(self.possible[rows][col])
        return block

    def validNumberInRow(self, number, index):
        return number not in self.numbers[index]
    
    def validNumberInColumn(self, number, index):
        return number not in self.getColumn(index)

    def validNumberInBlock(self, number, x, y):
        return number not in self.getBlock(x, y)

    def isValidNumber(self, num, row, col):
        return self.validNumberInRow(num, row) \
            and self.validNumberInColumn(num, col) \
            and self.validNumberInBlock(num, col//3, row//3)

    def backtrack(self, num, cellIndex):
        r,c = cellIndex//9, cellIndex%9
        if r > 8:
            return True
        while self.numbers[r][c] != 0:
            cellIndex += 1
            r,c = cellIndex//9, cellIndex%9
            if r > 8:
                return True # Every cell filled
        for num in range(num, 10):
            if not self.isValidNumber(num, r, c):
                continue
            self.numbers[r][c] = num
            print(self)
            if not self.backtrack(1, cellIndex + 1):
                continue
            else:
                return True
        self.numbers[r][c] = 0 # Backtrack
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

    def getBlockIndices(self, blockX, blockY, sudokuGrid = 9):
        """Return list of (row, col) indices in a block

        This is ambiguous indexing, so README
        block X,Y indices start from 0 to match list 0 indexing
        Max grid X,Y is sqrt(sudokuGrid)
        """
        blockSize = isqrt(sudokuGrid) # TODO Check for bad grid value (not even split 9,16,25)
        indices = []
        row0 = blockX * blockSize # 0, 1, 2 -> 0, 3, 6
        col0 = blockY * blockSize
        for row in range(row0, row0 + blockSize):
            for col in range(col0, col0 + blockSize):
                indices.append((row, col))
        return indices


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


    def trimPairsAndTriplets(self, sudokuGrid = 9):
        """

        1. Just loop through looking for matches
        2. Make lists of lengths to only look at others with same len
            But there's only 9 items per list
        """
        changes = 0
        # Rows
        for rowIndex, r in enumerate(self.possible):
            for i,c in enumerate(r):
                if len(c) == 2:
                    for j in range(i+1, len(r)):
                        if c == r[j]:
                            # Found a pair
                            # Should be the only pair, else maybe unsolveable?
                            for n in c:
                                changes += self.removeFromRow(n, rowIndex, exclude=[i,j])
                elif len(c) == 3:
                    for j in range(i+1, len(r)):
                        if c == r[j]:
                            # Found a pair, need to find a 3rd
                            for k in range(j+1, len(r)):
                                if c == r[k]:
                                    # Found triplet
                                    for n in c:
                                        changes += self.removeFromRow(n, rowIndex, exclude=[i,j,k])
        # Columns
        for colIndex in range(sudokuGrid):
            for rowIndex in range(sudokuGrid):
                c = self.possible[rowIndex][colIndex]
                if len(c) == 2:
                    for j in range(rowIndex+1, sudokuGrid):
                        if c == self.possible[j][colIndex]:
                            # Found a pair
                            # Should be the only pair, else maybe unsolveable?
                            for n in c:
                                changes += self.removeFromCol(n, colIndex, exclude=[rowIndex,j])
                elif len(c) == 3:
                    for j in range(rowIndex+1, sudokuGrid):
                        if c == self.possible[j][colIndex]:
                            # Found a pair, need to find a 3rd
                            for k in range(j+1, sudokuGrid):
                                if c == self.possible[k][colIndex]:
                                    # Found triplet
                                    for n in c:
                                        changes += self.removeFromCol(n, colIndex, exclude=[rowIndex,j,k])
        # Blocks
        nBlocks = isqrt(sudokuGrid)
        #TODO General: Is one faster nested for loops or flat loop with x = i//dim1 y = i%dim2 maybe z = i//(dim1*dim2), etc...
        for x in range(nBlocks):
            for y in range(nBlocks):
                indices = self.getBlockIndices(x, y, sudokuGrid)
                # DEBUG print block
                #print("Block",x,y)
                bchange = 0
                #self.printPossibleBlock(x, y)
                for i in range(len(indices)):
                    coordI = indices[i]
                    r,c = indices[i]
                    cell = self.possible[r][c]
                    if len(cell) == 2:
                        for j in range(i+1, len(indices)):
                            coordJ = indices[j]
                            rj, cj = indices[j]
                            if cell == self.possible[rj][cj]:
                                # Found a pair
                                # Should be the only pair, else maybe unsolveable?
                                for n in cell:
                                    cha= self.removeFromBlock(n, x, y, exclude=[coordI, coordJ])
                                    changes += cha
                                    bchange += cha
                    elif len(cell) == 3:
                        for j in range(i+1, len(indices)):
                            coordJ = indices[j]
                            rj, cj = indices[j]
                            if cell == self.possible[rj][cj]:
                                # Found a pair, find 3rd
                                for k in range(j+1, len(indices)):
                                    coordK = indices[k]
                                    rk, ck = indices[k]
                                    if cell == self.possible[rk][ck]:
                                        # Found triplet
                                        for n in cell:
                                            cha += self.removeFromBlock(n, x, y, exclude=[coordI, coordJ, coordK])
                                            changes += cha
                                            bchange += cha
                #if bchange > 0:
                #    print(bchange, 'changes')
                #    self.printPossibleBlock(x, y)
        return changes

    def playerSolver(self):
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
        "605000020",
        "000789003",
        "007005004",
        "000800210",
        "009010800",
        "021007000",
        "500100600",
        "300674000",
        "070000301",
            ]
    testBoard = [
            [int(x) for x in str(s)] for s in testBoard]
    print(testBoard)
    p0 = perf_counter()
    b = Board(testBoard)
    print(b)
    b.printPossible()
    b.playerSolver()
    print(b)
    pT = perf_counter() - p0
    b0 = perf_counter()
    b = Board(testBoard)
    print(b)
    b.printPossible()
    b.backtrack(1, 0)
    print(b)
    bT = perf_counter() - b0
    print("PlaySolver", pT)
    print("Backtrack", bT)
    print("Backtrack blank")
    b0 = perf_counter()
    b = Board([[0 for x in range(9)] for y in range(9)])
    print(b)
    b.backtrack(1, 0)
    print(b)
    bT = perf_counter() - b0
    print("Backtrack", bT)




if __name__ == "__main__":
    print("Howdy.")
    run()

