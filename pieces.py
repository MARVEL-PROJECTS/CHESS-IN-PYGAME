from enum import IntEnum
from itertools import cycle, islice, dropwhile, chain, product


class Colour(IntEnum):
    white = -1
    black = 1

class Piece:
    """
        Abstract class that outlines the common methods and fields
        for all chess pieces (Rook, Knight, Bishop, Queen, King, Pawn)
    """

    def __init__(self, position, colour):
        self.position = self.x, self.y = position
        self.colour = colour

    # returns a list of (x,y) such that the piece could move to those squares
    def getCanidiateSquares(self, board, in_check):
        raise NotImplementedError

    def getPath(self, fromCo, toCo):
        raise NotImplementedError

    def getBoard(self, candidate, board):        
        inGrid = lambda xy: xy[0] >= 0 and xy[1] >= 0 and xy[0] <= 7 and xy[1] <= 7
        print(candidate)
        assert(inGrid(candidate))
        return board[candidate[1]][candidate[0]]

    def isFree(self, candidate, board):
        inGrid = lambda xy: xy[0] >= 0 and xy[1] >= 0 and xy[0] <= 7 and xy[1] <= 7
        if(inGrid(candidate)):
            return board[candidate[1]][candidate[0]] is None
        else:
            return False
    
    def canCapture(self, candidate, board):
        inGrid = lambda xy: xy[0] >= 0 and xy[1] >= 0 and xy[0] <= 7 and xy[1] <= 7
        return (inGrid(candidate) and self.getBoard(candidate,board) != None and self.getBoard(candidate,board).colour != self.colour)

    # coords = index of square to move to
    def move(self, coords):
        self.position = coords
        self.x = coords[0]
        self.y = coords[1]


class Pawn(Piece):
    def __init__(self, position, colour):
        super().__init__(position, colour)
        self.hasMoved = False
    
    def getCanidiateSquares(self, board, in_check):
        direction = self.colour
        candidates = []

        forward = (self.x, self.y + direction)
        firstMove = (self.x, self.y + 2*direction)
        [leftDiag,rightDiag] = [(self.x - 1, self.y + direction), (self.x + 1, self.y + direction)]

        getBoard = lambda t: board[t[1]][t[0]]
        
        if(self.isFree(forward, board)):
            #TODO promote pawn
            candidates.append(forward)
        if(self.canCapture(leftDiag, board)):
            candidates.append(leftDiag)
        if(self.canCapture(rightDiag, board)):
            candidates.append(rightDiag)
        if not self.hasMoved: 
            candidates.append(firstMove)
        print(candidates)

        return candidates


    def getAttackingSquares(self):
        direction = self.colour
        return [(self.x - 1, self.y + direction), (self.x + 1, self.y + direction)]

    def getPath(self, fromCo, toCo):
        direction = self.colour
        path = []
        if fromCo[0] == toCo[0]:
            path += [(fromCo[0], fromCo[1] + direction)]
        if toCo[1] == fromCo[1] + 2:
            path += [(fromCo[0], fromCo[1] + 2*direction)]
        return path 

    def move(self, coords):
        super().move(coords)
        self.hasMoved = True

# p = Pawn((3, 3), Colour.white)
# print(p.getCanidiateSquares())


class Rook(Piece):
    def getCanidiateSquares(self, board, in_check):
        horizontal = [(self.x, y) for y in range(1, 9)]
        vertical = [(x, self.y) for x in range(1, 9)]
        candidates = horizontal + vertical
        legalMoves = list(filter(lambda candidate: self.isFree(candidate,board) or self.canCapture(candidate,board), candidates))
        legalAndNotBlocked = list(filter(lambda toPos: all(self.isFree(candidate, board) for candidate in self.getPath(self.position, toPos)), legalMoves))
        return legalAndNotBlocked
    
    def getPath(self, fromCo, toCo):
        (fromX, fromY) = fromCo
        (toX, toY) = toCo
        assert fromX == toX or fromY == toY 
        path = []
        if fromX == toX:
            if toY > fromY:
                path = [(fromX, fromY + i) for i in range(1, toY - fromY)]
            else: 
                path = [(fromX, fromY - i) for i in range(1, fromY - toY)]
        else:
            if toX > fromX:
                path = [(fromX + i, fromY) for i in range(1, toX - fromX)]
            else: 
                path = [(fromX - i, fromY) for i in range(1, fromX - toX)]

        return path

class Knight(Piece):
    def getCanidiateSquares(self, board, in_check):
        moves = product([1, -1], [2, -2])
        candidates = list(
            chain.from_iterable(
                [[(self.x + x, self.y + y), (self.x + y, self.y + x)] for (x, y) in moves]
            )
        )
        legalMoves = list(filter(lambda candidate: self.isFree(candidate,board) or self.canCapture(candidate,board), candidates))
        return legalMoves
    
    def getPath(self, fromCo, toCo):
        return []

class Bishop(Piece):
    def getCanidiateSquares(self, board, in_check):
        delta = [1, -1]
        diagonals = [
            (self.x + scale * x, self.y + scale * y)
            for (x, y) in product(delta, repeat=2)
            for scale in range(1, 8)
        ]
        candidates = diagonals
        legalMoves = list(filter(lambda candidate: self.isFree(candidate,board) or self.canCapture(candidate,board), candidates))
        legalAndNotBlocked = list(filter(lambda toPos: all(board[y][x] == None for (x,y) in self.getPath(self.position, toPos)), legalMoves))
        return legalAndNotBlocked

    def getPath(self, fromCo, toCo):
        (fromX, fromY) = fromCo
        (toX, toY) = toCo
        assert abs(fromX - toX) == abs(fromY - toY) 
        path = []
        pathLength = abs(fromX - toX)
        if toX > fromX:
            if toY > fromY:
                path = [(fromX + i, fromY + i) for i in range(1, pathLength)]
            else: 
                path = [(fromX + i, fromY - i) for i in range(1, pathLength)]
        else:
            if toY > fromY:
                path = [(fromX - i, fromY + i) for i in range(1, pathLength)]
            else: 
                path = [(fromX - i, fromY - i) for i in range(1, pathLength)]

        return path

class Queen(Piece):
    def getCanidiateSquares(self, board, in_check):
        tempBishopCandidates = Bishop(self.position, self.colour).getCanidiateSquares(board, in_check)
        tempRookCandidates = Rook(self.position, self.colour).getCanidiateSquares(board, in_check)
        candidates = tempBishopCandidates + tempRookCandidates
        print(candidates)
        return candidates

    def getPath(self, fromCo, toCo):
        bishop = Bishop(self.position, self.colour)
        rook = Rook(self.position, self.colour)
        if fromCo[0] == toCo[0] or fromCo[1] == toCo[1]:
            return rook.getPath(fromCo, toCo) 
        else:
            return bishop.getPath(fromCo, toCo)

class King(Piece):
    def __init__(self, position, colour):
        super().__init__(position, colour)
        self.inCheck = False

    def getCanidiateSquares(self, board, in_check):
        # TODO king needs to pnly be able to capture unprotected pieces
        delta = [-1, 0, 1]
        candidates = [(self.x + x, self.y + y) for (x, y) in product(delta, repeat=2)]
        candidates.remove(self.position)
        legalMoves = set(filter(lambda candidate:self.isFree(candidate,board) or self.canCapture(candidate,board), candidates)) 

        allAttackedSquares = set()
        for row in board:
            for piece in row:
                if piece != None and piece.colour != self.colour:
                    if isinstance(piece, King) or isinstance(piece, Pawn):
                        allAttackedSquares.update(piece.getAttackingSquares())
                    else:
                        allAttackedSquares.update(piece.getCanidiateSquares(board, in_check))

        
        legalAndNotAttacked = list(filter(lambda candidate: not (candidate in allAttackedSquares), legalMoves))

        return legalAndNotAttacked

    def getAttackingSquares(self):
        delta = [-1, 0, 1]
        candidates = [(self.x + x, self.y + y) for (x, y) in product(delta, repeat=2)]
        candidates.remove(self.position)
        return candidates

    def getPath(self, fromCo, toCo):
        return []
    
    def putInCheck(self):
        self.inCheck = True

    def outOfCheck(self):
        self.inCheck = False
