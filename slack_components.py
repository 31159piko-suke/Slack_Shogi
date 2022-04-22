import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from collections import defaultdict


def generate_board(
    ban: list,
    teban_motigoma: list = [],
    unteban_motigoma: list = [],
    sashite: list = [0, 0],
    y: int = 32 * 2,
    x: int = 32 * 2,
):
    board = Image.open("./images/board.jpg")
    board = board.resize((800 * 2, 640 * 2))
    board = np.array(board)[:, :, :3]
    suzi, dan = 8 - sashite[0], 8 - sashite[1]

    for i in range(9):
        for j in range(9):
            koma = ban[i][j] if not (suzi == i and dan == j) else str(ban[i][j]) + "_"
            if koma == 0:
                continue
            koma = Image.open(f"./images/{koma}.jpg")
            koma = koma.resize((56 * 2, 60 * 2))
            koma = np.array(koma)

            board[
                y + 64 * i * 2 : y + 64 * i * 2 + 5,
                200 + x + 60 * j * 2 + 5 : 200 + x + 60 * j * 2 + koma.shape[1] - 6,
            ] = koma[:5, 7:-4]
            board[
                y + 64 * i * 2 + 5 : 64 * i * 2 + y + koma.shape[0] - 5,
                200 + x + 60 * j * 2 + 5 : 200 + x + 60 * j * 2 + koma.shape[1] - 6,
            ] = koma[5:-5, 7:-4]
            board[
                y + 64 * i * 2 + koma.shape[0] - 5 : y + 64 * i * 2 + koma.shape[0],
                200 + x + 60 * j * 2 + 5 : 200 + x + 60 * j * 2 + koma.shape[1] - 6,
            ] = koma[-5:, 7:-4]

    tmp_dict = defaultdict(int)
    for i in teban_motigoma:
        tmp_dict[i] += 1
    motigoma_dict = dict(sorted(tmp_dict.items()))
    for i, koma in enumerate(motigoma_dict.items()):
        board[1140 - 120 * i : 1140 - 120 * i + 128, 1420 : 1420 + 120] = np.array(
            Image.open(f"./images/_{koma[0]}.jpg").resize((60 * 2, 64 * 2))
        )
        board[1140 - 120 * i : 1140 - 120 * i + 68, 1530 : 1530 + 44] = np.array(
            Image.open(f"./images/no{koma[1]}.jpg").resize((22 * 2, 34 * 2))
        )

    tmp_dict = defaultdict(int)
    for i in unteban_motigoma:
        tmp_dict[i] += 1
    motigoma_dict = dict(sorted(tmp_dict.items()))
    for i, koma in enumerate(motigoma_dict.items()):
        board[20 + 120 * i : 20 + 120 * i + 128, 20 : 20 + 120] = np.array(
            Image.open(f"./images/_-{koma[0]}.jpg").resize((60 * 2, 64 * 2))
        )
        board[20 + 120 * i : 20 + 120 * i + 68, 135 : 135 + 44] = np.array(
            Image.open(f"./images/no{koma[1]}.jpg").resize((22 * 2, 34 * 2))
        )

    fig = plt.figure(figsize=(15, 15))
    plt.imshow(board)
    plt.axis("off")
    fig.savefig("/tmp/img.png", bbox_inches="tight", pad_inches=0)


def compress_status(
    ban: list,
    teban_motigoma: list,
    unteban_motigoma: list,
    teban: str,
    unteban: str,
    sashite: list = [-1, -1],
    tesu: int = 0,
):
    ban = str(ban).replace("[", "").replace("]", "").replace(" ", "")
    teban_motigoma = (
        str(teban_motigoma).replace("[", "").replace("]", "").replace(" ", "")
    )
    unteban_motigoma = (
        str(unteban_motigoma).replace("[", "").replace("]", "").replace(" ", "")
    )

    sashite = [8 - i for i in sashite[:2]]
    sashite = str(sashite).replace("[", "").replace("]", "").replace(" ", "")
    tesu = str(tesu)

    status = "/".join(
        [ban, teban_motigoma, unteban_motigoma, teban, unteban, sashite, tesu]
    )
    return status


def deconpress_status(status: str):
    status_ = status.split("/")
    ban = np.array(
        [[int(i) for i in status_[0].split(",")][i : i + 9] for i in range(0, 81, 9)]
    )
    teban_motigoma = [int(i) for i in status_[1].split(",")] if status_[1] else []
    unteban_motigoma = [int(i) for i in status_[2].split(",")] if status_[2] else []
    teban = status_[3]
    unteban = status_[4]
    last_sashite = [int(i) for i in status_[5].split(",")] if status_[5] else [0, 0]
    tesu = int(status_[6]) + 1
    return ban, teban_motigoma, unteban_motigoma, teban, unteban, last_sashite, tesu


def generate_block(
    url: str, block_id: str, teban: str, sashite: str = "", tesu: int = 0
):
    block = [
        {
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": f"{tesu}手目 {sashite}",
                "emoji": True,
            },
            "image_url": url,
            "alt_text": f"{tesu}手目 {sashite}",
        },
        {
            "type": "input",
            "block_id": block_id,
            "dispatch_action": True,
            "element": {
                "type": "plain_text_input",
                "action_id": "plain_text_input-action",
                "dispatch_action_config": {"trigger_actions_on": ["on_enter_pressed"]},
            },
            "label": {"type": "plain_text", "text": f"{teban} の手番じゃ！", "emoji": True},
        },
    ]
    return block
