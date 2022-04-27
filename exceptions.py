class InputBaseError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.message}"


class ShogiBaseError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.message}"


class UndefinedFugoError(InputBaseError):
    def __init__(self, message="正しく符号を入力しましょう！"):
        super().__init__(message)


class UndefinedMomaError(InputBaseError):
    def __init__(self, message="駒を指定していませんよ？"):
        super().__init__(message)


class InvalidInputError(InputBaseError):
    def __init__(self, message="正しく入力しましょう！"):
        super().__init__(message)


class KomaAlreadyExistError(ShogiBaseError):
    def __init__(self, message="そこにはすでに駒がありますよ！"):
        super().__init__(message)


class KomaCannotMoveError(ShogiBaseError):
    def __init__(self, message="そこには動けませんよ！持ち駒を使う場合は「◯◯打」と入力してください！"):
        super().__init__(message)


class KomaCannotNariError(ShogiBaseError):
    def __init__(self, message="おっと、まだその駒は成れないようです..."):
        super().__init__(message)


class MultipleKomaCanMoveError(ShogiBaseError):
    def __init__(self, message="複数の駒がそのマスに移動できるみたいです。上、引、寄、左、右、直などを指定指定してください！"):
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
    def __init__(self, message="成らないと動けなくなりますよ！"):
        super().__init__(message)
