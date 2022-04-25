from exceptions import UndefinedMomaError, UndefinedFugoError


class ParseInput:
    def __init__(self):
        pass

    def parse(self, sashite: str, last_sashite: list):
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

        suzi, dan, sashite = self.valid_fugo(sashite)
        koma, sashite = self.valid_koma(sashite)
        dousa, sashite = self.valid_dousa(sashite)
        iti, sashite = self.valid_iti(sashite)
        nari, sashite = self.valid_nari(sashite)
        return [suzi, dan, koma, dousa, iti, nari]

    def valid_fugo(self, sashite: str):
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
        """
        fugo_dict = {
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
        if sashite[0] == "同":  # ex) 同銀
            suzi, dan = self.last_sashite
            return suzi, dan, sashite[1:]

        elif len(sashite) >= 2:  # ex) 76歩
            if fugo_dict.get(sashite[0]) and fugo_dict.get(sashite[1]):
                suzi, dan = fugo_dict.get(sashite[0]), fugo_dict.get(sashite[1])
                suzi, dan = dan - 1, 9 - suzi
                if len(sashite) >= 3 and sashite[2] == "同":  # ex) 88同銀
                    if suzi == self.last_sashite[0] and dan == self.last_sashite[1]:
                        return suzi, dan, sashite[3:]
                    raise UndefinedFugoError
                return suzi, dan, sashite[2:]
            raise UndefinedFugoError
        raise UndefinedFugoError

    def valid_koma(self, sashite: str):
        """
        For example:
        input:
            sashite : "歩"
        output:
            "歩", ""

        input:
            sashite : "金左"
        output:
            "金", "左"
        """
        koma_dict = {
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
        for i in range(len(sashite)):
            if koma_dict.get(sashite[: i + 1]):
                return koma_dict.get(sashite[: i + 1]), sashite[i + 1 :]
        raise UndefinedMomaError

    def valid_dousa(self, sashite: str):
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
        """
        dousa_dict = {"上": 1, "引": 2, "寄": 3}
        if sashite:
            if dousa_dict.get(sashite[0]):
                return dousa_dict.get(sashite[0]), sashite[1:]
            return dousa_dict.get(sashite[0]), sashite
        return None, None

    def valid_iti(self, sashite: str):
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
        """
        iti_dict = {"左": 1, "右": 2, "直": 3}
        if sashite:
            if iti_dict.get(sashite[0]):
                return iti_dict.get(sashite[0]), sashite[1:]
            return iti_dict.get(sashite[0]), sashite
        return None, None

    def valid_nari(self, sashite: str):
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
        """
        nari_dict = {"成": 1, "不成": 2, "打": 3}
        if sashite:
            for i in range(len(sashite)):
                if nari_dict.get(sashite[i:]):
                    return nari_dict.get(sashite[i:]), sashite[i:]
            return nari_dict.get(sashite[i:]), sashite
        return None, None
