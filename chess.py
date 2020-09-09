import pygame
import copy
import numpy as np
import pieces
from pieces import Colour, Piece, Pawn, Rook, Knight, Bishop, Queen, King
WIDTH = int
HEIGHT = int

class Chess:
    """
        Chess - Models the systems of logic involved in a chess game
    """

    def __init__(self):
        self.turn_colour = Colour.white
        self.board = []
        self.is_over = False
        

    def on_init(self):
        pawnRow = lambda y, c: [Pawn((x, y), c) for x in range(8)]
        constructPieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        pieceRow = lambda y, c: [constructPieces[x]((x, y), c) for x in range(8)]
        emptyRow = [None, None, None, None, None, None, None, None]
        for y in range(8):
            row = emptyRow.copy()
            if y == 0:
                row = pieceRow(y, Colour.black)
            elif y == 7:
                row = pieceRow(y, Colour.white)
            elif y == 1:
                row = pawnRow(y, Colour.black)
            elif y == 6:
                row = pawnRow(y, Colour.white)
            self.board.append(row)

    def move(self, fromPos, toPos):
        # Tries to move a piece from square with coordinates fromPos to square toPos
        # Returns True if a legal move occured and False otherwise

        # TODO: handle en passaunt

        (fromX, fromY) = fromPos
        (toX, toY) = toPos
        fromPiece = self.board[fromY][fromX]

        if fromPiece is None or (fromPiece.colour != self.turn_colour):
            return False
        
        (white_in_check, black_in_check) = self.evaluate_checks(self.board)

        in_check = 0 
        if fromPiece.colour == Colour.white: 
            in_check = white_in_check
        else: 
            in_check = black_in_check

        candidates = fromPiece.getCanidiateSquares(self.board, in_check )
        isLegal = toPos in candidates

        # TODO blocking dosnt work
        copyBoard = copy.deepcopy(self.board)
        copyFromPiece = copyBoard[fromY][fromX]
        copyBoard[fromY][fromX] = None
        copyBoard[toY][toX] = copyFromPiece
        copyFromPiece.move(toPos)
        (white_in_check, black_in_check) = self.evaluate_checks(copyBoard)

        in_check = 0
        if self.turn_colour == Colour.white:
            in_check = white_in_check
        else: 
            in_check = black_in_check
        
        isLegal = isLegal and not(in_check)

        if isLegal:
            self.board[fromY][fromX] = None
            self.board[toY][toX] = fromPiece
            fromPiece.move(toPos)
            self.turn_colour *= -1 

        return isLegal

    def evaluate_checks(self, board):
        white_in_check = False 
        black_in_check = False 

        white_king = 0
        black_king = 0
        for row in board:
            for piece in row:
                if isinstance(piece, King) and piece.colour == Colour.white:
                    white_king = piece
                if isinstance(piece, King) and piece.colour == Colour.black:
                    black_king = piece
        for row in board:
            for piece in row: 
                if piece != None and piece.colour == Colour.white: 
                    if black_king.position in piece.getCanidiateSquares(self.board, False):
                        black_in_check = True 
                elif piece != None and piece.colour == Colour.black:
                    if white_king.position in piece.getCanidiateSquares(self.board, False):
                        white_in_check = True
        return (white_in_check, black_in_check)