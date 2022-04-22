import numpy as np
from exceptions import (
    KomaAlreadyExistError,
    KomaCannotMoveError,
    KomaCannotNariError,
    MultipleKomaCanMoveError,
    UnidentifiedNariFunariError,
    DonotHaveMotigomaError,
    CannotUseMotigomaError,
    OteIgnorError,
    FunariError,
)


class InitGame:
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
        if nari == 3:  # 持ち駒を打つなら
            if (not self.is_teban_koma(y, x)) and (
                not self.is_unteban_koma(y, x)
            ):  # 駒がないかを確認
                if self.is_motigoma(koma):  # 持ち駒にあるかを確認
                    if self.is_goho_utu(y, x, koma):  # 二歩や動けないマスにおいていないかを確認
                        self.use_motigoma(y, x, koma)  # 持ち駒を打つ
                        if not self.is_ote():  # 王手放置してないか確認
                            self.board = np.flip(self.board) * (-1)  # 相手に手番が周り、盤面が入れ替わる
                            self.teban_motigoma, self.unteban_motigoma = (
                                self.unteban_motigoma,
                                self.teban_motigoma,
                            )  # 持ち駒も入れ替える
                        else:
                            raise OteIgnorError
                    else:
                        raise CannotUseMotigomaError
                else:
                    raise DonotHaveMotigomaError
            else:
                raise KomaAlreadyExistError

        else:  # 盤上の駒を動かすなら
            if not self.is_teban_koma(y, x):  # 自分の駒がないかを確認
                res = self.is_goho_move(y, x, koma, dousa, iti, nari)
                if res:  # 入力が合法手か確認
                    dy, dx = res
                    self.remove_koma(y + dy, x - dx)  # 元居たところから駒を消す
                    self.move_koma(y, x, koma, nari)  # 入力通りに駒を動かす,相手の駒があるなら持ち駒にする、成り不成も
                    if not self.is_ote():  # 王手放置してないか確認
                        self.board = np.flip(self.board) * (-1)  # 相手に手番が周り、盤面が入れ替わる
                        self.teban_motigoma, self.unteban_motigoma = (
                            self.unteban_motigoma,
                            self.teban_motigoma,
                        )  # 持ち駒も入れ替える
                    else:
                        raise OteIgnorError
            else:
                raise KomaAlreadyExistError

    def is_goho_move(
        self,
        y: int,
        x: int,
        koma: int,
        dousa: int = None,
        iti: int = None,
        nari: int = None,
    ):  # 合法手であるかを確認
        candi_dy, candi_dx = [], []
        action_candidates_list = np.array(self.action_dict[koma], dtype=object)
        if dousa:
            action_candidates_list = action_candidates_list * self.dousa[dousa]
        if iti:
            action_candidates_list = action_candidates_list * self.iti[iti]
        print(list(action_candidates_list))
        for i, j in enumerate(action_candidates_list):
            for moving_length in j:
                if koma == 3:  # 桂馬だけ別の処理
                    dy, dx = moving_length
                else:
                    dy, dx = self.directions[i] * moving_length
                if (y + dy >= 0) and (x - dx >= 0) and (y + dy <= 8) and (x - dx <= 8):
                    print(dy, dx)
                    print(self.board[y + dy][x - dx])
                    if self.board[y + dy][x - dx] == koma:  # 駒が見つかればその方向は探索を打ち切る
                        candi_dy.append(dy)
                        candi_dx.append(dx)
                        break
                    elif self.is_teban_koma(y + dy, x - dx) or self.is_unteban_koma(
                        y + dy, x - dx
                    ):  # 探索途中で間に駒がある方向は探索を打ち切る
                        break
        if len(candi_dy) == 0 and len(candi_dx) == 0:  # そこに動かせる駒があるか
            raise KomaCannotMoveError

        elif len(candi_dy) >= 2 and len(candi_dx) >= 2:  # 動かせる駒があるとき、唯一の駒か
            raise MultipleKomaCanMoveError

        else:
            dy, dx = candi_dy[0], candi_dx[0]
            if ((koma == 1 or koma == 2) and y == 0 and nari != 1) or (
                koma == 3 and y <= 1 and nari != 1
            ):  # 動けなくならないように成る
                raise FunariError

            if (
                (y <= 2 or y + dy <= 2) and nari is None and abs(koma) < 10
            ):  # 敵陣に出入りしたとき成不成が指定されているか
                raise UnidentifiedNariFunariError

            if y >= 3 and y + dy >= 3 and nari == 1:  # 成れないのに成ろうとしてないか
                raise KomaCannotNariError

            return (dy, dx)

    def is_goho_utu(self, y: int, x: int, koma: int):
        return (not self.is_nifu(x, koma)) and (self.can_utigoma_move(y, koma))

    def is_nifu(self, x: int, koma: int):
        if koma == 1:
            for i in range(self.board.shape[0]):
                if self.board[i][x] == 1:
                    return True
        return False

    def can_utigoma_move(self, y: int, koma: int):
        if (koma == 1 or koma == 2) and (y == 0):
            return False
        elif koma == 3 and y <= 1:
            return False
        else:
            return True

    def is_motigoma(self, koma: int):
        return True if koma in self.teban_motigoma else False

    def use_motigoma(self, y: int, x: int, koma: int):
        self.teban_motigoma.remove(koma)
        self.board[y][x] = koma

    def get_motigoma(self, koma: int):
        self.teban_motigoma.append(int(str(koma)[-1]))

    def move_koma(self, y: int, x: int, koma: int, nari: int = None):
        if self.is_unteban_koma(y, x):  # 移動先に相手の駒があったら持ち駒にする
            self.get_motigoma(self.board[y][x])
        self.board[y][x] = koma + 10 if nari == 1 and y <= 2 else koma  # 成るときは成る

    def remove_koma(self, y: int, x: int):
        self.board[y][x] = 0

    def is_ote(self):
        y, x = self.get_gyoku_position()
        if (
            self.board[y - 2][x + 1] == -3 or self.board[y - 2][x - 1] == -3
        ):  # 桂馬だけ先にチェック
            return True
        for i, (edy, edx) in enumerate(self.directions):
            for j in range(1, self.board.shape[0]):
                dy, dx = edy * j, edx * j
                # print(dy,dx)
                if (y - dy >= 0) and (x + dx >= 0) and (y - dy <= 8) and (x + dx <= 8):
                    print(y - dy, x + dx)
                    ote_candi_koma = [
                        -k for k, v in self.action_dict.items() if j in v[i]
                    ]
                    print(ote_candi_koma)
                    if self.board[y - dy][x + dx] in ote_candi_koma:
                        return True
                    if self.is_teban_koma(y - dy, x + dx) or self.is_unteban_koma(
                        y - dy, x + dx
                    ):
                        break
        return False

    def get_gyoku_position(self):
        for y in range(self.board.shape[0]):
            for x in range(self.board.shape[1]):
                if self.board[y][x] == 8:
                    gyoku_position = (y, x)
        return gyoku_position

    def is_teban_koma(self, y: int, x: int):  # 自分の駒がいるかチェック
        return True if self.board[y][x] > 0 else False

    def is_unteban_koma(self, y: int, x: int):  # 相手の駒がいるかチェック
        return True if self.board[y][x] < 0 else False
