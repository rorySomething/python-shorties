#! python3

"""
Menace Tic tac toe

Matchbox represents board state
  Including all mirrors and rotations
  E.g. All in 1 box
  .x. ... ... ...
  ... ..x ... x..
  ... ... .x. ...
  Rotations & mirrors


Matchbox contains beads, 1 for each possible move.
Randomly pick a bead to decide next move.
Draw, add 1 bead to each move/box used.
Win, add 3 of each bead chosen to each box used.
Lose, remove the 1 of each beads used.

Moves will just be a list counter
beads[0] = # of beads for placing in top left
total odds = sum(beads)
choice = random(total odds)
"""

from enum import IntEnum
from random import choice
import matplotlib.pyplot as plt

boards = {}
"""
Board is represented as 18 bits in an int
9 board positions
1 bit occupied
2 bit 1 is X, 0 is O
So bit shift >> | 3 => X in space
bit shift >> | 2 => O in space
"""
class Matchbox:
    startingBeads = 50
    def __init__(self):
        self.layout = 0 # 18 bits
        self.symmetric = set()
        self.beadsX = [x for x in range(9)]*Matchbox.startingBeads
        # 001122334455667788
        # 2 of each bead, to choose
        self.beadsO = [x for x in range(9)]*Matchbox.startingBeads

    def clearInvalidMoves(self):
        b = intToBoard(self.layout)
        for i in range(9):
            if b[i] != '':
                while i in self.beadsX:
                    self.beadsX.remove(i)
                while i in self.beadsO:
                    self.beadsO.remove(i)


def addMatchbox(number, boards, bset = set()):
    if number not in boards:
        boards[number] = Matchbox()
        boards[number].layout = number
        boards[number].symmetric = bset
        boards[number].clearInvalidMoves()

def boardToInt(board):
    """board is array of X or O"""
    n = 0
    for p in board[::-1]: # Loop backwards
        if p == '':
            n <<= 2 # 2   0's
            continue
        n |= 1
        n <<= 1
        if p == 'X':
            n |= 1
        n <<= 1
    n >>= 1
    return n

def intToBoard(n):
    board = []
    for i in range(9):
        val = n & 3
        n >>= 2
        if val == 3:
            board.append('X')
        elif val == 2:
            board.append('O')
        else:
            board.append('')
    return board

def printBoard(board):
    print(f"""
             {board[0]:>1} | {board[1]:>1} | {board[2]:>1}
            ---+---+---
             {board[3]:>1} | {board[4]:>1} | {board[5]:>1}
            ---+---+---
             {board[6]:>1} | {board[7]:>1} | {board[8]:>1}""")

def rotate(boardNumber):
    b = intToBoard(boardNumber)
    # 012   630
    # 345 = 741
    # 678   852
    b[0], b[1], b[2], b[5], b[8], b[7], b[6], b[3] = b[6], b[3], b[0], b[1], b[2], b[5], b[8], b[7]
    return boardToInt(b)

def mirror0(boardNumber):
    """Horizontal"""
    b = intToBoard(boardNumber)
    # 012   678
    # 345 = 345
    # 678   012
    b[0], b[1], b[2], b[6], b[7], b[8] = b[6], b[7], b[8], b[0], b[1], b[2]
    return boardToInt(b)

def mirror1(boardNumber):
    """Vertical"""
    b = intToBoard(boardNumber)
    # 012   210
    # 345 = 543
    # 678   876
    b[0], b[2], b[3], b[5], b[6], b[8] = b[2], b[0], b[5], b[3], b[8], b[6]
    return boardToInt(b)

def mirror2(boardNumber):
    """Diagonal /"""
    b = intToBoard(boardNumber)
    # 012   852
    # 345 = 741
    # 678   630
    b[0], b[1], b[3], b[5], b[7], b[8] = b[8], b[5], b[7], b[1], b[3], b[0]
    return boardToInt(b)
    
def mirror3(boardNumber):
    """Diagonal \\"""
    b = intToBoard(boardNumber)
    # 012   036
    # 345 = 147
    # 678   258
    b[1], b[2], b[3], b[5], b[6], b[7] = b[3], b[6], b[1], b[7], b[2], b[5]
    return boardToInt(b)

def getOperations(ref, target):
    ops = []
    r = ref
    for x in range(3):
        r = rotate(r)
        ops.append(0)
        if r == target:
            return ops
    ops = [1]
    r = mirror0(ref) # horizontal reflection
    if r == target:
        return ops
    for x in range(3):
        r = rotate(r)
        ops.append(0)
        if r == target:
            return ops
    ops = [2]
    r = mirror1(ref) # vertical reflection
    if r == target:
        return ops
    for x in range(3):
        r = rotate(r)
        ops.append(0)
        if r == target:
            return ops
    ops = [3]
    r = mirror2(ref) # diagonal reflection /
    if r == target:
        return ops
    for x in range(3):
        r = rotate(r)
        ops.append(0)
        if r == target:
            return ops
    ops = [4]
    r = mirror3(ref) # diagonal reflection \\
    if r == target:
        return ops
    for x in range(3):
        r = rotate(r)
        ops.append(0)
        if r == target:
            return ops
    raise RuntimeError(f"Unrelated boards are grouped {ref} {target}")

# Dictionary results of sym operations
symOps = {
    0:{ # rot
        0:2,
        1:5,
        2:8,
        3:1,
        5:7,
        6:0,
        7:3,
        8:6
    },
    1:{ # horizontal mirror
        0:6,
        1:7,
        2:8,
        6:0,
        7:1,
        8:2
    },
    2:{ # vert
        0:2,
        2:0,
        3:5,
        5:3,
        6:8,
        8:6
    },
    3:{ # diag /
        0:8,
        1:5,
        3:7,
        5:1,
        7:3,
        8:0
    },
    4:{ # diag \\
        1:3,
        2:6,
        3:1,
        5:7,
        6:2,
        7:5
    }
    }

def applyOps(choice, ops):
    """Move a 3x3 grid position by rotation or mirroring"""
    c = choice
    for o in ops:
        if c in symOps[o]:
            c = symOps[o][c]
    return c



def transform(choice, referenceBoard, playBoard):
    """Matchbox beads are for the matchbox ref board.
    Need to rotate/reflect the choice to the play board."""
    if choice == 4 or referenceBoard == playBoard: # Center unchanging
        return choice
    ops = getOperations(referenceBoard, playBoard)
    return applyOps(choice, ops)

def getBoardSet(boardNumber):
    s = set()
    a = boardNumber
    b = mirror0(a)
    c = mirror1(a)
    d = mirror2(a)
    e = mirror3(a)
    s |= set([a,b,c,d,e])
    for i in range(3):
        a = rotate(a)
        b = rotate(b)
        c = rotate(c)
        d = rotate(d)
        e = rotate(e)
        s |= set([a,b,c,d,e])
    return min(s), s

class GameResult(IntEnum):
    PLAY = 0
    DRAW = 1
    X = 2
    O = 3


def checkBoard(boardNumber):
    b = intToBoard(boardNumber)
    if b[0] == b[4] == b[8] == '':
        return GameResult.PLAY
    r0 = b[:3]
    r1 = b[3:6]
    r2 = b[6:]
    c0 = b[::3]
    c1 = b[1::3]
    c2 = b[2::3]
    d0 = b[::4]
    d1 = b[2:7:2]
    openMove = False
    for x in (r0, r1, r2, c0, c1, c2, d0, d1):
        nX = x.count('X')
        if nX == 3:
            return GameResult.X
        nO = x.count('O')
        if nO == 3:
            return GameResult.O
        nB = x.count('')
        if nB > 1 or nX == 0 or nO == 0:
            openMove = True
        if nB == 1 and (nX == 2 or nO == 2):
            openMove = True
    if not openMove:
        return GameResult.DRAW
    return GameResult.PLAY

def updateBoard(char, board, pos):
    b = intToBoard(board)
    if b[pos] != '':
        print(char, pos)
        raise RuntimeError("Position occupied")
    b[pos] = char
    return boardToInt(b)


class PlayerType(IntEnum):
    CHUMP = 1
    BOT = 2

def getInt(minV, maxV):
    while True:
        x = input("Enter choice: ")
        try:
            x = int(x)
        except:
            continue
        if x >= minV and x <= maxV:
            return x
        else:
            print(f"Must choose {minV} to {maxV}")

def promptTurn(board, char):
    print("Choose where to place", char)
    b = intToBoard(board)
    printBoard(b)
    choices = [i for i in range(9) if b[i] == '']
    choice = -1
    while choice not in choices:
        print(" ".join([str(x) for x in choices]))
        choice = getInt(min(choices), max(choices))
    return choice

def menaceChoose(board, boards, isX):
    b, bset = getBoardSet(board) # Get common symmetry
    if b not in boards:
        addMatchbox(b, boards, bset)
    if isX:
        #print(set(boards[b].beadsX))
        try:
            c = choice(boards[b].beadsX)
        except:
            print(set(boards[b].beadsX))
            printBoard(intToBoard(board))
            raise
        return transform(c, b, board)
    else:
        #print(set(boards[b].beadsO))
        try:
            c = choice(boards[b].beadsO)
        except:
            print(set(boards[b].beadsO))
            printBoard(intToBoard(board))
            raise
        return transform(c, b, board)

def plot(beadList, O):
    plt.subplots()
    zero = beadList[0]
    y = [b-zero for b in beadList]
    x = list(range(1, len(beadList)+1))
    plt.plot(x, y, 'bx', label='X')
    zero = O[0]
    y = [b-zero for b in O]
    x = list(range(1, len(O)+1))
    plt.plot(x, y, 'ro', label='O')
    plt.legend()
    plt.title("Menace")
    plt.ylabel("beads 3xwin + draws - loses")
    plt.xlabel("games")
    plt.savefig('menace.png')

def plotBoards(n):
    plt.subplots()
    y = n
    x = list(range(1, len(n)+1))
    plt.plot(x, y, 'b.', label='Boards')
    plt.title("Menace Symmetry Reduced Boards Played On")
    plt.ylabel("Boards")
    plt.xlabel("Games")
    plt.savefig('menaceboards.png')



def prompt():
    print("Tic tac toe MENACE")
    print("Who plays first as X?")
    print("1. You,  2. Computer")
    first = getInt(1, 2)
    print("Who goes second as O?")
    print("1. You,  2. Computer")
    second = getInt(1, 2)
    if first == second == 2:
        print("Computer battle!")
    print("How many rounds?")
    rounds = getInt(1, 999999999)
    return (first,second,rounds)

def play(A, B, rounds, quiet = False, debug = True):
    print(f"Players {PlayerType(A).name} v {PlayerType(B).name}  {rounds} rounds  Go!")
    boards = {} # Holds matchboxes
    # Tracking results for plotting
    box0Beads = []
    results = []
    box1Beads = []
    box1s = []
    nb = []
    for i in range(9):
        box1s.append(3 << (2*i))
    played = 0
    while played < rounds:
        # Entire game here
        played += 1
        firstPlayer = True # False in 2nd player's turn
        Xmoves = []
        Omoves = []
        state = GameResult.PLAY
        board = 0
        beads = 0
        for v in boards.values():
            beads += len(v.beadsX) + len(v.beadsO)
        if not quiet:
            print(f"Played: {played}, boards: {len(boards)}, beads: {beads}")
        # move = (board, placement)
        while state == GameResult.PLAY:
            # Take turns until finished
            #printBoard(intToBoard(board))

            b, bset = getBoardSet(board) # Get common symmetry
            # Save moves using base/ref symmetry board
            if firstPlayer:
                choice = -1
                basec = -1
                if A == PlayerType.CHUMP:
                    choice = promptTurn(board, 'X')
                else:
                    choice = menaceChoose(board, boards, isX=True)
                Xmoves.append((b, transform(choice, board, b)))
                board = updateBoard('X', board, choice)
            else:
                choice = -1
                if B == PlayerType.CHUMP:
                    choice = promptTurn(board, 'O')
                else:
                    choice = menaceChoose(board, boards, isX=False)
                Omoves.append((b, transform(choice, board, b)))
                board = updateBoard('O', board, choice)
            state = checkBoard(board)
            firstPlayer = not firstPlayer # Switch turn
        # Process results
        if state == GameResult.DRAW:
            if not quiet:
                print("DRAW!")
                printBoard(intToBoard(board))
            results.append(0)
            # Add 1 bead to all choices
            for x in Xmoves:
                b, pos = x
                if b not in boards:
                    addMatchbox(b, boards)
                boards[b].beadsX.append(pos)
            for o in Omoves:
                b, pos = o
                if b not in boards:
                    addMatchbox(b, boards)
                boards[b].beadsO.append(pos)
        elif state == GameResult.X:
            if not quiet:
                print("X won!")
                printBoard(intToBoard(board))
            # Add 3 beads to all choices
            results.append(1)
            for x in Xmoves:
                b, pos = x
                if b not in boards:
                    addMatchbox(b, boards)
                boards[b].beadsX.append(pos)
                boards[b].beadsX.append(pos)
                boards[b].beadsX.append(pos)
            # Remove 1 bead of all choices
            for o in Omoves:
                b, pos = o
                if b not in boards:
                    addMatchbox(b, boards)
                boards[b].beadsO.remove(pos)
        else: # Assume O wins
            if not quiet:
                print("O won!")
                printBoard(intToBoard(board))
            results.append(2)
            # Remove 1 bead of all choices
            for x in Xmoves:
                b, pos = x
                if b not in boards:
                    addMatchbox(b, boards)
                boards[b].beadsX.remove(pos)
            # Add 3 beads to all choices
            for o in Omoves:
                b, pos = o
                if b not in boards:
                    addMatchbox(b, boards)
                boards[b].beadsO.append(pos)
                boards[b].beadsO.append(pos)
                boards[b].beadsO.append(pos)
        box0Beads.append(len(boards[0].beadsX))
        nb.append(len(boards))
        box1 = 0
        for i in box1s:
            if i not in boards:
                addMatchbox(i, boards)
            box1 += len(boards[i].beadsO)
        box1Beads.append(box1)
    plot(box0Beads, box1Beads)
    plotBoards(nb)




if __name__ == "__main__":
    import sys
    quiet = False
    if '-q' in sys.argv:
        quiet = True
        print("Quiet!")
    p1, p2, rounds = 2,2,400
    try:
        rounds = int(sys.argv[-1])
    except:
        p1, p2, rounds = prompt()
    play(p1, p2, rounds, quiet)
