from exceptions import UndefinedMomaError, UndefinedFugoError, InvalidInputError


class Input:
    def __init__(self):
        self.fugo_dict = {
            "一": 1,
            "１": 1,
            "1": 1,
            "二": 2,
            "２": 2,
            "2": 2,
            "三": 3,
            "３": 3,
            "3": 3,
            "四": 4,
            "４": 4,
            "4": 4,
            "五": 5,
            "５": 5,
            "5": 5,
            "六": 6,
            "６": 6,
            "6": 6,
            "七": 7,
            "７": 7,
            "7": 7,
            "八": 8,
            "８": 8,
            "8": 8,
            "九": 9,
            "９": 9,
            "9": 9,
        }
        self.koma_dict = {
            "歩": 1,
            "と": 11,
            "香": 2,
            "成香": 12,
            "桂": 3,
            "成桂": 13,
            "銀": 4,
            "成銀": 14,
            "金": 5,
            "角": 6,
            "馬": 16,
            "飛": 7,
            "龍": 17,
            "竜": 17,
            "玉": 8,
            "王": 8,
        }
        self.dousa_dict = {"上": 1, "引": 2, "寄": 3, "": 0}
        self.iti_dict = {"左": 1, "右": 2, "直": 3, "": 0}
        self.nari_dict = {"成": 1, "不成": 2, "打": 3, "": 0}

    def parse(self, sashite: str, last_sashite: list) -> list:
        """
        For example:
        input:
            sashite : "76歩"
        output:
            [5, 2, 1, None, None, None]

        input:
            sashite : "58金左"
        output:
            [7, 4, 5, None, 1, None]

        input:
            sashite : "４六角打つ"
        output:
            [5, 5, 6, None, None, 3]
        """
        self.last_sashite = last_sashite
        replace_list = [
            "香車",
            "桂馬",
            "銀将",
            "金将",
            "角行",
            "飛車",
            "王将",
            "玉将",
            "と金",
            "成香車",
            "成桂馬",
            "成銀将",
            "成り",
            "不成り",
            "打ち",
            "打つ",
        ]
        for i in replace_list:
            sashite = sashite.replace(i, i[:-1])

        suzi, dan, sashite = self._valid_fugo(sashite)
        koma, sashite = self._valid_koma(sashite)
        dousa, sashite = self._valid_dousa(sashite)
        iti, sashite = self._valid_iti(sashite)
        nari, sashite = self._valid_nari(sashite)
        if sashite:
            raise InvalidInputError

        return [suzi, dan, koma, dousa, iti, nari]

    def format(self, parsed_sashite, tesu):
        """
        For example:
        input:
            parsed_sashite : [5, 2, 1, None, None, None]
        output:
            '76歩'
        """
        sashite = [int(i) if i not in ["None", None] else 0 for i in parsed_sashite]
        if len(sashite) > 3:
            sente_suzi = str(9 - sashite[1]) if tesu % 2 == 0 else str(1 + sashite[1])
            sente_dan = str(1 + sashite[0]) if tesu % 2 == 0 else str(9 - sashite[0])
            gote_suzi = str(1 + sashite[1]) if tesu % 2 == 0 else str(9 - sashite[1])
            gote_dan = str(9 - sashite[0]) if tesu % 2 == 0 else str(1 + sashite[0])

            koma = [
                key for key, value in self.koma_dict.items() if value == sashite[2]
            ][0]
            dousa = [
                key for key, value in self.dousa_dict.items() if value == sashite[3]
            ][0]
            iti = [key for key, value in self.iti_dict.items() if value == sashite[4]][
                0
            ]
            nari = [
                key for key, value in self.nari_dict.items() if value == sashite[5]
            ][0]
            return (
                "".join([sente_suzi, sente_dan, koma, dousa, iti, nari])
                + " ("
                + "".join([gote_suzi, gote_dan, koma, dousa, iti, nari])
                + ")"
            )
        else:
            return ""

    def _valid_fugo(self, sashite: str) -> tuple:
        """
        For example:
        input:
            sashite : "76歩"
        output:
            5, 2, "歩"

        input:
            sashite : "58金左"
        output:
            7, 4, "金左"

        input:
            sashite : "４六角打"
        output:
            5, 5, "角打"
        """
        if sashite[0] == "同":  # ex) 同銀
            suzi, dan = self.last_sashite
            return suzi, dan, sashite[1:]

        elif len(sashite) >= 2:  # ex) 76歩
            if self.fugo_dict.get(sashite[0]) and self.fugo_dict.get(sashite[1]):
                suzi, dan = self.fugo_dict.get(sashite[0]), self.fugo_dict.get(
                    sashite[1]
                )
                suzi, dan = dan - 1, 9 - suzi
                if len(sashite) >= 3 and sashite[2] == "同":  # ex) 88同銀
                    if suzi == self.last_sashite[0] and dan == self.last_sashite[1]:
                        return suzi, dan, sashite[3:]
                    raise InvalidInputError
                return suzi, dan, sashite[2:]
            raise UndefinedFugoError
        raise UndefinedFugoError

    def _valid_koma(self, sashite: str) -> tuple:
        """
        For example:
        input:
            sashite : "歩"
        output:
            1, ""

        input:
            sashite : "金左"
        output:
            5, "左"

        input:
            sashite : "角打"
        output:
            6, "打"
        """
        for i in range(len(sashite)):
            if self.koma_dict.get(sashite[: i + 1]):
                return self.koma_dict.get(sashite[: i + 1]), sashite[i + 1 :]
        raise UndefinedMomaError

    def _valid_dousa(self, sashite: str) -> tuple:
        """
        For example:
        input:
            sashite : ""
        output:
            None, None

        input:
            sashite : "左"
        output:
            None, "左"

        input:
            sashite : "打"
        output:
            None, "打"
        """
        if sashite:
            if self.dousa_dict.get(sashite[0]):
                return self.dousa_dict.get(sashite[0]), sashite[1:]
            return None, sashite
        return None, None

    def _valid_iti(self, sashite: str) -> tuple:
        """
        For example:
        input:
            sashite : None
        output:
            None, None

        input:
            sashite : "左"
        output:
            1, ""

        input:
            sashite : "打"
        output:
            None, "打"
        """
        if sashite:
            if self.iti_dict.get(sashite[0]):
                return self.iti_dict.get(sashite[0]), sashite[1:]
            return None, sashite
        return None, None

    def _valid_nari(self, sashite: str) -> tuple:
        """
        For example:
        input:
            sashite : None
        output:
            None, None

        input:
            sashite : ""
        output:
            None, None

        input:
            sashite : "打"
        output:
            3, []
        """
        if sashite:
            for i in range(len(sashite)):
                if self.nari_dict.get(sashite[: i + 1]):
                    return self.nari_dict.get(sashite[: i + 1]), sashite[i + 1 :]
            return None, sashite
        return None, None
