import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from collections import defaultdict


def generate_board_image(
    user: str,
    ts: str,
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
            koma = koma.resize((54 * 2, 58 * 2))
            koma = np.array(koma)

            board[
                y + 128 * i + 2 : y + 128 * i + koma.shape[0] + 2,
                200 + x + 120 * j + 5 : 200 + x + 120 * j + koma.shape[1] - 3,
            ] = koma[:, 5:-3]

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
    fig.savefig(f"/tmp/{user}:{ts}.jpg", bbox_inches="tight", pad_inches=0)


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

    sashite = sashite
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
    last_sashite = [i for i in status_[5].split(",")] if status_[5] else [-1, -1]
    tesu = int(status_[6])
    return ban, teban_motigoma, unteban_motigoma, teban, unteban, last_sashite, tesu


def generate_board_block(
    teban_user: str,
    unteban_user: str,
    url: str,
    block_id: str,
    user: str,
    tesu: int = 0,
    sashite: str = "",
    is_end: bool = False,
    winner: str = "",
):
    block = [
        init_section(teban_user, unteban_user),
        image_section(url, tesu, sashite),
        button_section(is_end),
        input_section(block_id, user),
    ]
    end_block = [
        init_section(teban_user, unteban_user),
        image_section(url, tesu, sashite),
        button_section(is_end),
        end_section(block_id, winner),
    ]
    return end_block if is_end else block


def init_section(teban_user, unteban_user):
    section = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*先手   <@{teban_user}> *    vs    * <@{unteban_user}>   後手*",
        },
    }
    return section


def image_section(url: str, tesu: str, sashite: str):
    section = {
        "type": "image",
        "title": {
            "type": "plain_text",
            "text": f"{tesu}手目 {sashite}",
            "emoji": True,
        },
        "image_url": url,
        "alt_text": f"{tesu}手目 {sashite}",
    }
    return section


def button_section(is_end: bool = False):
    section = {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "投了", "emoji": True},
                "action_id": "button_lose_confirm-action",
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "再表示", "emoji": True},
                "action_id": "button_show-action",
            },
        ],
    }
    end_section = {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "再表示", "emoji": True},
                "action_id": "button_show-action",
            },
        ],
    }

    return end_section if is_end else section


def input_section(block_id: str, user: str):
    section = {
        "type": "input",
        "block_id": block_id,
        "dispatch_action": True,
        "element": {
            "type": "plain_text_input",
            "action_id": "plain_text_input_update-action",
            "dispatch_action_config": {"trigger_actions_on": ["on_enter_pressed"]},
        },
        "label": {
            "type": "plain_text",
            "text": f"<@{user}> の手番です！",
            "emoji": True,
        },
    }
    return section


def end_section(block_id: str, winner: str):
    section = {
        "type": "section",
        "block_id": block_id,
        "text": {
            "type": "mrkdwn",
            "text": f"*<@{winner}> の勝ちです！！*",
        },
    }
    return section


def generate_ephemeral_block(ts: str, status: str):
    block = [
        {
            "type": "section",
            "block_id": ":".join([ts, status]),
            "text": {"type": "mrkdwn", "text": "本当に投了しますか？"},
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "はい", "emoji": True},
                "action_id": "button_lose-action",
            },
        }
    ]
    return block
