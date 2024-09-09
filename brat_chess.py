from PyQt5 import QtWidgets, QtGui, QtCore
from enum import Enum

chess_pieces = {"king": "\u265A", "queen": "\u265B", "rook": "\u265C", "knight": "\u265E", "pawn": "\u265F"}
white_square_color = QtGui.QColor(138, 206, 0)
black_square_color = QtGui.QColor(117, 117, 117)
white_brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
black_brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
size = 6


class GameState(Enum):
    whites_turn = "whites_turn"
    blacks_turn = "blacks_turn"
    white_selected = "white_selected"
    black_selected = "black_selected"
    white_win = "white_win"
    black_win = "black_win"


class ChessGame(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("brat chess")
        self.setGeometry(0, 0, 800, 800)
        self.setStyleSheet("background-color: white; color: black;")
        self.grid = self.create_board()
        self.populate_board_6x6()
        self.text = QtWidgets.QLabel("it's white's turn. select which piece to move.")
        self.grid.clicked.connect(self.clicked)
        self.game_state = GameState.whites_turn
        self.selected_piece = (-1, -1)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.grid)
        self.layout.addWidget(self.text)
        self.setLayout(self.layout)
        self.show()

    def clicked(self, item):
        position = (item.column(), item.row())
        if self.game_state == GameState.whites_turn:
            if self.valid_piece(*position):
                self.text.setText("it's white's turn. select where you want to move the piece.")
                self.game_state = GameState.white_selected
                self.selected_piece = position
        elif self.game_state == GameState.blacks_turn:
            if self.valid_piece(*position):
                self.text.setText("it's black's turn. select where you want to move the piece.")
                self.game_state = GameState.black_selected
                self.selected_piece = position
        elif self.game_state == GameState.white_selected:
            if position in self.valid_moves(*self.selected_piece):
                if self.game_piece_type(*self.selected_piece) == "rook":
                    self.swap_pieces(*self.selected_piece, *position)
                else:
                    self.move_piece(*self.selected_piece, *position)
                if self.check_win():
                    self.text.setText("white won!")
                    self.game_state = GameState.white_win
                else:
                    self.text.setText("it's black's turn. select which piece to move.")
                    self.game_state = GameState.blacks_turn
            else:
                self.text.setText("it's white's turn. that is not a valid move.")
        elif self.game_state == GameState.black_selected:
            if position in self.valid_moves(*self.selected_piece):
                if self.game_piece_type(*self.selected_piece) == "rook":
                    self.swap_pieces(*self.selected_piece, *position)
                else:
                    self.move_piece(*self.selected_piece, *position)
                if self.check_win():
                    self.text.setText("black won!")
                    self.game_state = GameState.black_win
                else:
                    self.text.setText("it's white's turn. select which piece to move.")
                    self.game_state = GameState.whites_turn
            else:
                self.text.setText("it's black's turn. that is not a valid move.")

    def move_piece(self, x0: int, y0: int, x1: int, y1: int):
        item = self.grid.item(y0, x0)
        self.place_piece(text=item.text(), color=item.foreground(), x=x1, y=y1)
        item.setText("")

    def swap_pieces(self, x0: int, y0: int, x1: int, y1: int):
        item0_text = self.grid.item(y0, x0).text()
        item0_color = self.grid.item(y0, x0).foreground()
        item1_text = self.grid.item(y1, x1).text()
        item1_color = self.grid.item(y1, x1).foreground()
        self.place_piece(text=item0_text, color=item0_color, x=x1, y=y1)
        self.place_piece(text=item1_text, color=item1_color, x=x0, y=y0)

    def is_available(self, x: int, y: int, player_color: QtGui.QBrush) -> bool:
        opponent_color = white_brush if player_color == black_brush else black_brush
        return self.is_empty(x, y) or self.grid.item(y, x).foreground() == opponent_color

    def is_empty(self, x: int, y: int) -> bool:
        return self.grid.item(y, x).text() == ""

    def check_win(self) -> bool:
        num_kings = 0
        for i in range(size):
            for j in range(size):
                if self.game_piece_type(i, j) == "king":
                    num_kings += 1
        return num_kings < 2

    def place_piece(self, text: str, color: QtGui.QBrush, x: int, y: int):
        item = self.grid.item(y, x)
        item.setText(text)
        item.setForeground(color)

    @staticmethod
    def in_range(x: int, y: int) -> bool:
        return 0 <= x < size and 0 <= y < size

    def valid_piece(self, x: int, y: int) -> bool:
        piece = self.grid.item(y, x)
        return (piece.text() != "" and len(self.valid_moves(x, y)) > 0 and
                ((self.game_state == GameState.whites_turn and piece.foreground() == white_brush) or
                 (self.game_state == GameState.blacks_turn and piece.foreground() == black_brush)))

    def game_piece_type(self, x: int, y: int) -> str:
        # returns the type of game piece given a char representing the piece (ex. "\u265A" -> "king")
        text = self.grid.item(y, x).text()
        return next((piece_type for piece_type, unicode in chess_pieces.items() if unicode == text), "")

    def valid_moves(self, x: int, y: int) -> list:
        # provided the current location of a piece, return valid next moves

        piece = self.grid.item(y, x)
        piece_type = self.game_piece_type(x, y)

        moves = []
        if piece_type == "king":
            moves.extend([(x-1, y), (x+1, y)])
        elif piece_type == "queen":
            for i in range(x-2, x+2+1):
                for j in range(y-2, y+2+1):
                    moves.append((i, j))
        elif piece_type == "knight":
            moves.extend([(x-2, y), (x+2, y), (x, y-2), (x, y+2)])
        elif piece_type == "rook":
            for i in range(0, size):
                for j in range(0, size):
                    if self.grid.item(i, j).foreground() == piece.foreground():
                        moves.append((j, i))
            return moves  # we know all these moves are valid, so we don't need to check if they're in range and valid
        elif piece_type == "pawn":
            moves.extend([(x, y-1), (x, y+1)])
        valid_moves_list = []
        for move in moves:
            if self.in_range(*move) and self.is_available(*move, piece.foreground()):
                valid_moves_list.append(move)

        return valid_moves_list

    def create_board(self):
        grid = QtWidgets.QTableWidget(size, size)
        grid.setRowCount(size)
        grid.setColumnCount(size)
        font = self.font()
        font.setPointSize(60)
        for i in range(size):
            for j in range(size):
                grid.setItem(i, j, QtWidgets.QTableWidgetItem(""))
                grid.item(i, j).setTextAlignment(QtCore.Qt.AlignCenter)
                grid.item(i, j).setFont(font)
                grid.item(i, j).setBackground(white_square_color if (i + j) % 2 == 0 else black_square_color)
        grid.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        grid.horizontalHeader().hide()
        grid.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        grid.verticalHeader().hide()
        return grid

    def populate_board_6x6(self):
        # populates 6x6 board with game pieces at correct starting positions

        # set white pieces at starting positions
        self.place_piece(text=chess_pieces["rook"], color=white_brush, x=0, y=0)
        self.place_piece(text=chess_pieces["knight"], color=white_brush, x=1, y=0)
        self.place_piece(text=chess_pieces["queen"], color=white_brush, x=2, y=0)
        self.place_piece(text=chess_pieces["king"], color=white_brush, x=3, y=0)
        self.place_piece(text=chess_pieces["knight"], color=white_brush, x=4, y=0)
        self.place_piece(text=chess_pieces["rook"], color=white_brush, x=5, y=0)
        for i in range(6):
            self.place_piece(text=chess_pieces["pawn"], color=white_brush, x=i, y=1)

        # set black pieces at starting positions
        self.place_piece(text=chess_pieces["rook"], color=black_brush, x=0, y=5)
        self.place_piece(text=chess_pieces["knight"], color=black_brush, x=1, y=5)
        self.place_piece(text=chess_pieces["queen"], color=black_brush, x=2, y=5)
        self.place_piece(text=chess_pieces["king"], color=black_brush, x=3, y=5)
        self.place_piece(text=chess_pieces["knight"], color=black_brush, x=4, y=5)
        self.place_piece(text=chess_pieces["rook"], color=black_brush, x=5, y=5)
        for i in range(6):
            self.place_piece(text=chess_pieces["pawn"], color=black_brush, x=i, y=4)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = ChessGame()
    app.exec()
