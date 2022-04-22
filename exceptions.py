class ParseInputBaseError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.message}"


class ShogiBaseError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.message}"


class UndefinedFugoError(ParseInputBaseError):
    def __init__(self, message="符号を正しく入力しましょう！"):
        super().__init__(message)


class UndefinedMomaError(ParseInputBaseError):
    def __init__(self, message="動かす駒を指定していませんよ？"):
        super().__init__(message)


class KomaAlreadyExistError(ShogiBaseError):
    def __init__(self, message="そこにはすでに駒がありますよ！"):
        super().__init__(message)


class KomaCannotMoveError(ShogiBaseError):
    def __init__(self, message="そこには動けませんよ！"):
        super().__init__(message)


class KomaCannotNariError(ShogiBaseError):
    def __init__(self, message="おっと、まだその駒は成れません..."):
        super().__init__(message)


class MultipleKomaCanMoveError(ShogiBaseError):
    def __init__(self, message="複数の駒がそのマスに移動できるみたいです。上、引、寄、左、右、直などを指定しましょう！"):
        super().__init__(message)


class UnidentifiedNariFunariError(ShogiBaseError):
    def __init__(self, message="成りますか？成りませんか？"):
        super().__init__(message)


class DonotHaveMotigomaError(ShogiBaseError):
    def __init__(self, message="いつから駒を持っていると錯覚しました...？"):
        super().__init__(message)


class CannotUseMotigomaError(ShogiBaseError):
    def __init__(self, message="そこには打てません！"):
        super().__init__(message)


class OteIgnorError(ShogiBaseError):
    def __init__(self, message="王手...かかってるよ..."):
        super().__init__(message)


class FunariError(ShogiBaseError):
    def __init__(self, message="成らないと動けなくなります！"):
        super().__init__(message)
