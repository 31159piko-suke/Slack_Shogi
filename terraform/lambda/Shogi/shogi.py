import numpy as np
from exceptions import (
    KomaAlreadyExistError,
    KomaCannotMoveError,
    KomaCannotNariError,
    MultipleKomaCanMoveError,
    UnidentifiedNariFunariError,
    CannnotidentifiedNariFunariError,
    DonotHaveMotigomaError,
    CannotUseMotigomaError,
    OteIgnorError,
    FunariError,
)


class InitGame:
    """
    <Class InitGame>

    Initialize the board and motigoma.

    Attributes
    ----------
    board:
        It is a Board.

    teban_motigoma:
        Komas owned by the user who are on turn.

    unteban_motigoma:
        Komas owned by the user who are not on turn.
    """

    def __init__(self):
        self.board = np.array(
            [
                [-2, -3, -4, -5, -8, -5, -4, -3, -2],
                [0, -7, 0, 0, 0, 0, 0, -6, 0],
                [-1, -1, -1, -1, -1, -1, -1, -1, -1],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1, 1],
                [0, 6, 0, 0, 0, 0, 0, 7, 0],
                [2, 3, 4, 5, 8, 5, 4, 3, 2],
            ]
        )
        self.teban_motigoma = []
        self.unteban_motigoma = []


class KomaActions:
    """
    <Class KomaActions>

    Define the movement of komas.

    Attributes
    ----------
    action_dict:
        Defines the eight directions of movement for the koma.
        Each index in the list defines the number that can be advanced in that direction.
        But `桂` is exception to the rule.

        For example:
        2 1 0
        3 歩 7  -> [[], [1], [], [], [], [], [], []]
        4 5 6

        2 1 0
        3 金 7  -> [[1], [1], [1], [1], [], [1], [], [1]]
        4 5 6

    dousa:
        `dousa` is an additive option that specifies the movement of the koma.

    iti:
        `iti` is an additive option that specifies the movement of the koma.

    directions:
        A list defining each direction, defined for implementation convenience.
    """

    def __init__(self):
        self.action_dict = {
            1: [[], [1], [], [], [], [], [], []],  # 歩
            2: [[], [1, 2, 3, 4, 5, 6, 7, 8], [], [], [], [], [], []],  # 香
            3: [[(2, 1)], [], [(2, -1)], [], [], [], [], []],  # 桂
            4: [[1], [1], [1], [], [1], [], [1], []],  # 銀
            5: [[1], [1], [1], [1], [], [1], [], [1]],  # 金
            6: [
                [1, 2, 3, 4, 5, 6, 7, 8],
                [],
                [1, 2, 3, 4, 5, 6, 7, 8],
                [],
                [1, 2, 3, 4, 5, 6, 7, 8],
                [],
                [1, 2, 3, 4, 5, 6, 7, 8],
                [],
            ],  # 角
            7: [
                [],
                [1, 2, 3, 4, 5, 6, 7, 8],
                [],
                [1, 2, 3, 4, 5, 6, 7, 8],
                [],
                [1, 2, 3, 4, 5, 6, 7, 8],
                [],
                [1, 2, 3, 4, 5, 6, 7, 8],
            ],  # 飛
            8: [[1], [1], [1], [1], [1], [1], [1], [1]],  # 玉
            11: [[1], [1], [1], [1], [], [1], [], [1]],  # と金
            12: [[1], [1], [1], [1], [], [1], [], [1]],  # 成香
            13: [[1], [1], [1], [1], [], [1], [], [1]],  # 成桂
            14: [[1], [1], [1], [1], [], [1], [], [1]],  # 成銀
            16: [
                [1, 2, 3, 4, 5, 6, 7, 8],
                [1],
                [1, 2, 3, 4, 5, 6, 7, 8],
                [1],
                [1, 2, 3, 4, 5, 6, 7, 8],
                [1],
                [1, 2, 3, 4, 5, 6, 7, 8],
                [1],
            ],  # 馬
            17: [
                [1],
                [1, 2, 3, 4, 5, 6, 7, 8],
                [1],
                [1, 2, 3, 4, 5, 6, 7, 8],
                [1],
                [1, 2, 3, 4, 5, 6, 7, 8],
                [1],
                [1, 2, 3, 4, 5, 6, 7, 8],
            ],  # 龍
        }
        self.dousa = {
            1: [True, True, True, False, False, False, False, False],  # 上
            2: [False, False, False, False, True, True, True, False],  # 引
            3: [False, False, False, True, False, False, False, True],  # 寄
        }
        self.iti = {
            1: [True, False, False, False, False, False, True, True],  # 左
            2: [False, False, True, True, True, False, False, False],  # 右
            3: [False, True, False, False, False, False, False, False],  # 直
        }
        self.directions = [
            np.array((1, 1)),
            np.array((1, 0)),
            np.array((1, -1)),
            np.array((0, -1)),
            np.array((-1, -1)),
            np.array((-1, 0)),
            np.array((-1, 1)),
            np.array((0, 1)),
        ]


class Shogi:
    """
    <Class Shogi>

    Manage the board and the motigoma.
    """

    def __init__(
        self, board=None, teban_motigoma: list = None, unteban_motigoma: list = None
    ):
        if board is None:
            self.initgame = InitGame()
            self.board = self.initgame.board
            self.teban_motigoma = self.initgame.teban_motigoma
            self.unteban_motigoma = self.initgame.unteban_motigoma
        else:
            self.board = board
            self.teban_motigoma = teban_motigoma
            self.unteban_motigoma = unteban_motigoma

        self.kifuaction = KomaActions()
        self.action_dict = self.kifuaction.action_dict
        self.dousa = self.kifuaction.dousa
        self.iti = self.kifuaction.iti
        self.directions = self.kifuaction.directions

    def action(
        self,
        y: int,
        x: int,
        koma: int,
        dousa: int = None,
        iti: int = None,
        nari: int = None,
    ):
        """
        Params
        ------
        y : int
        x : int
        koma : int
            歩:1, 香:2, 桂:3, 銀:4, 金:5 ,角:6 , 飛:7, 玉:8,
            と金:11 , 成香:12, 成桂:13, 成銀:14, 馬:16 ,龍:17
        dousa : int, default None
            上:1, 引:2, 寄:3
        iti : int, default None
            左:1, 右:2, 直:3
        nari : int, default None
            成:1, 不成:2, 打:3
        """
        if nari == 3:  # if use a motigoma
            if (not self._is_teban_koma(y, x)) and (not self._is_unteban_koma(y, x)):
                if self._is_motigoma(koma):
                    if self._is_legal_utu(y, x, koma):
                        self._use_motigoma(y, x, koma)
                        if not self._is_ote():
                            # if it's legal move, the turn goes to the opponent.
                            self.board = np.flip(self.board) * (-1)
                            self.teban_motigoma, self.unteban_motigoma = (
                                self.unteban_motigoma,
                                self.teban_motigoma,
                            )
                        else:
                            raise OteIgnorError
                    else:
                        raise CannotUseMotigomaError
                else:
                    raise DonotHaveMotigomaError
            else:
                raise KomaAlreadyExistError

        else:  # if move a koma on the board
            if not self._is_teban_koma(y, x):
                dy, dx = self._is_legal_move(y, x, koma, dousa, iti, nari)
                self._remove_koma(y + dy, x - dx)
                self._move_koma(y, x, koma, nari)
                if not self._is_ote():
                    # if it's legal move, the turn goes to the opponent.
                    self.board = np.flip(self.board) * (-1)
                    self.teban_motigoma, self.unteban_motigoma = (
                        self.unteban_motigoma,
                        self.teban_motigoma,
                    )
                else:
                    raise OteIgnorError
            else:
                raise KomaAlreadyExistError

    def _is_legal_move(
        self,
        y: int,
        x: int,
        koma: int,
        dousa: int = None,
        iti: int = None,
        nari: int = None,
    ) -> tuple:
        """
        Search the eight directions around the specified position (y, x)
        and check it is legal move and which koma is moved.

        Return
        ------
        dy : int
            How many squares the koma will be moved on the y-axis.
        dx : int
            How many squares the koma will be moved on the x-axis.
        """
        candi_dy, candi_dx = [], []
        action_candidates_list = np.array(self.action_dict[koma], dtype=object)
        if dousa:  # if dousa is specified, narrow the search direction.
            action_candidates_list = action_candidates_list * self.dousa[dousa]
        if iti:  # if iti is specified, narrow the search direction.
            action_candidates_list = action_candidates_list * self.iti[iti]

        for i, j in enumerate(action_candidates_list):
            for moving_length in j:  # ex) j=[1], j=[1,2,3,4,5,6,7,8], j=[(2, 1)]
                if koma == 3:  # if koma is `桂`
                    dy, dx = moving_length  # dx, dy = 2, 1 or 2, -1
                else:
                    dy, dx = self.directions[i] * moving_length

                if (y + dy >= 0) and (x - dx >= 0) and (y + dy <= 8) and (x - dx <= 8):
                    if self.board[y + dy][x - dx] == koma:  # if the koma is found
                        candi_dy.append(dy)
                        candi_dx.append(dx)
                        break
                    elif self._is_teban_koma(y + dy, x - dx) or self._is_unteban_koma(
                        y + dy, x - dx
                    ):

                        # if other koma is found, the search in that direction is terminated.
                        break

        if len(candi_dy) == 0 and len(candi_dx) == 0:
            raise KomaCannotMoveError

        elif len(candi_dy) >= 2 and len(candi_dx) >= 2:
            raise MultipleKomaCanMoveError

        else:
            dy, dx = candi_dy[0], candi_dx[0]
            if not self._can_move_koma(y, koma, nari):
                raise FunariError

            if (
                (y <= 2 or y + dy <= 2)
                and (nari is None)
                and (koma not in [5, 8, 11, 12, 13, 14, 16, 17])
            ):
                raise UnidentifiedNariFunariError

            if (koma in [5, 8, 11, 12, 13, 14, 16, 17]) and (nari is not None):
                raise CannnotidentifiedNariFunariError

            if y >= 3 and y + dy >= 3 and nari == 1:
                raise KomaCannotNariError

            return (dy, dx)

    def _is_legal_utu(self, y: int, x: int, koma: int) -> bool:
        """
        Check if it is a legal move when using motigoma.

        Return
        ------
        bool
        """
        return (not self._is_nifu(x, koma)) and (self._can_move_koma(y, koma))

    def _is_nifu(self, x: int, koma: int) -> bool:
        """
        Check if not 二歩.

        Return
        ------
        bool
        """
        if koma == 1:
            for i in range(self.board.shape[0]):
                if self.board[i][x] == 1:
                    return True
        return False

    def _can_move_koma(self, y: int, koma: int, nari: int) -> bool:
        """
        Check if the koma can move.

        Return
        ------
        bool
        """
        if (koma == 1 or koma == 2) and (y == 0) and (nari != 1):
            return False
        elif koma == 3 and y <= 1 and (nari != 1):
            return False
        else:
            return True

    def _is_motigoma(self, koma: int) -> bool:
        """
        Check if you have the koma.

        Return
        ------
        bool
        """
        return True if koma in self.teban_motigoma else False

    def _use_motigoma(self, y: int, x: int, koma: int) -> None:
        """
        Use motigoma.

        Return
        ------
        None
        """
        self.teban_motigoma.remove(koma)
        self.board[y][x] = koma

    def _add_motigoma(self, koma: int) -> None:
        """
        Add the koma to motigoma.

        Return
        ------
        None
        """
        self.teban_motigoma.append(int(str(koma)[-1]))

    def _move_koma(self, y: int, x: int, koma: int, nari: int = None) -> None:
        """
        Move the koma.
        If there is an opponent's koma, add that koma to motigoma.

        Return
        ------
        None
        """
        if self._is_unteban_koma(y, x):
            self._add_motigoma(self.board[y][x])
        self.board[y][x] = koma + 10 if nari == 1 else koma

    def _remove_koma(self, y: int, x: int) -> None:
        """
        Remove the koma from its previous position (if moving the koma on the board).

        Return
        ------
        None
        """
        self.board[y][x] = 0

    def _is_ote(self) -> bool:
        """
        Search the eight directions around the `玉`(8)
        and check if there is a koma that can put `玉`(8) in check.

        ex1:
        if i == 0 and j == 1, ote_cande_koma=[-4, -5, -6, -11, -12, -13, -14, -16, -17]
        □ □ -4    □ □ -5    □ □ -6
        □ 8 □     □ 8 □     □ 8 □
        □ □ □  ,  □ □ □  ,  □ □ □  ...

        ex2:
        if i == 1 and j == 1, ote_cande_koma=[-1, -2, -4, -5, -7, -11, -12, -13, -14, -16, -17]
        □ -1 □    □ -2 □    □ -4 □
        □ 8 □     □ 8 □     □ 8 □
        □ □ □  ,  □ □ □  ,  □ □ □  ...

        ex3:
        if i == 5 and j == 1, ote_cande_koma=[-5, -7, -11, -12, -13, -14, -16, -17]
        □ □ □      □ □ □      □ □ □
        □ 8 □      □ 8 □      □ 8 □
        □ -5 □  ,  □ -7 □  ,  □ -11 □  ...

        ex4:
        if i == 0 and j == 2, ote_cande_koma=[-6, -16]
        □ □ □ -6    □ □ □ -16
        □ □ □ □     □ □ □ □
        □ 8 □ □     □ 8 □ □
        □ □ □ □  ,  □ □ □ □


        Return
        ------
        bool
        """
        y, x = self._get_gyoku_position()
        if self.board[y - 2][x + 1] == -3 or self.board[y - 2][x - 1] == -3:  # 桂
            # ex:
            # □ □ -3    -3 □ □
            # □ □ □     □ □ □
            # □ 8 □  ,  □ 8 □
            return True

        for i, (edy, edx) in enumerate(self.directions):
            for j in range(1, self.board.shape[0]):
                dy, dx = edy * j, edx * j
                if (y - dy >= 0) and (x + dx >= 0) and (y - dy <= 8) and (x + dx <= 8):
                    ote_candi_koma = [
                        -k for k, v in self.action_dict.items() if j in v[i]
                    ]
                    if self.board[y - dy][x + dx] in ote_candi_koma:
                        return True
                    if self._is_teban_koma(y - dy, x + dx) or self._is_unteban_koma(
                        y - dy, x + dx
                    ):
                        # if other koma is found, the search in that direction is terminated.
                        break
        return False

    def _get_gyoku_position(self) -> tuple:
        """
        Get the position of "玉"(8).

        Return
        ------
        gyoku_position : tuple
            Tuple of index where `玉`(8) is.
        """
        for y in range(self.board.shape[0]):
            for x in range(self.board.shape[1]):
                if self.board[y][x] == 8:
                    gyoku_position = (y, x)
        return gyoku_position

    def _is_teban_koma(self, y: int, x: int) -> bool:
        """
        Check if own koma is there.

        Return
        -----
        bool
        """
        return True if self.board[y][x] > 0 else False

    def _is_unteban_koma(self, y: int, x: int) -> bool:
        """
        Check if opponent's koma is there.

        Return
        ------
        bool
        """
        return True if self.board[y][x] < 0 else False
