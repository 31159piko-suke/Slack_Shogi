import os
import re
import numpy as np
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

from s3 import put_s3_and_get_url
from exceptions import ParseInputBaseError, ShogiBaseError
from slack_components import (
    generate_board_image,
    generate_board_block,
    generate_ephemeral_block,
    compress_status,
    deconpress_status,
)
from parse_input import ParseInput
from shogi import Shogi

app = App(
    process_before_response=True,
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)


def lambda_handler(event, context):
    if event["headers"].get("X-Slack-Retry-Num", False):
        return {"statusCode": 200, "body": "no need retry"}
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)


@app.event("app_mention")
def say_hello(ack, say, body, client):
    ack()
    channel = body["event"]["channel"]
    user = body["event"]["user"]
    ts = body["event"]["ts"]

    message = body["event"]["text"]
    opponent = re.findall(r"<@[A-Z0-9]{9}>", message)

    if len(opponent) != 1:
        say("対戦相手を一人選んでメンションしてください", replace_original=False)
    else:
        user_dict = {0: user, 1: opponent[0][2:-1]}

        hurigoma = int((np.random.random() * 2 // 1))
        teban_user = user_dict[hurigoma]
        unteban_user = user_dict[hurigoma ^ 1]

        try:
            _ = client.users_profile_get(user=teban_user)["profile"]
            _ = client.users_profile_get(user=unteban_user)["profile"]
        except:
            say("対戦相手を一人選んでメンションしてください", replace_original=False)
        else:
            say(f"*先手   <@{teban_user}> *    vs    * <@{unteban_user}>   後手*")

            shogi = Shogi()
            ban = shogi.board.tolist()
            teban_motigoma = shogi.teban_motigoma
            unteban_motigoma = shogi.unteban_motigoma

            generate_board_image(user, ts, ban)
            url = put_s3_and_get_url(user, ts)
            status = compress_status(
                ban, teban_motigoma, unteban_motigoma, teban_user, unteban_user
            )

            say(
                channel=channel,
                text="shogi",
                blocks=generate_board_block(url, status, teban_user),
            )


def arc_func(ack):
    ack()


def update(respond, body, client):
    channel = body["channel"]["id"]
    user = body["user"]["id"]
    ts = body["message"]["ts"]
    status = body["actions"][0]["block_id"]
    sashite = body["actions"][0]["value"]

    (
        ban,
        teban_motigoma,
        unteban_motigoma,
        teban_user,
        unteban_user,
        last_sashite,
        tesu,
    ) = deconpress_status(status)

    if user == teban_user:
        try:
            parseinput = ParseInput()
            persed_sashite = parseinput.parse(sashite, last_sashite)
        except ParseInputBaseError as e:
            respond(str(e), replace_original=False)
        else:
            shogi = Shogi(ban, teban_motigoma, unteban_motigoma)
            try:
                shogi.action(*persed_sashite)
                tesu += 1
            except ShogiBaseError as e:
                respond(str(e), replace_original=False)
            else:
                teban_user, unteban_user = unteban_user, teban_user
                ban = shogi.board.tolist()
                teban_motigoma = shogi.teban_motigoma
                unteban_motigoma = shogi.unteban_motigoma

                generate_board_image(
                    user, ts, ban, teban_motigoma, unteban_motigoma, persed_sashite
                )
                url = put_s3_and_get_url(user, ts)
                status = compress_status(
                    ban,
                    teban_motigoma,
                    unteban_motigoma,
                    teban_user,
                    unteban_user,
                    persed_sashite,
                    tesu,
                )
                client.chat_update(
                    channel=channel,
                    ts=ts,
                    blocks=generate_board_block(
                        url, status, teban_user, tesu=tesu, sashite=sashite
                    ),
                    text=f"{tesu}手目 {sashite}",
                )
    else:
        respond(f"<@{teban_user}> の手番です", replace_original=False)


def lose_confirm(respond, body):
    user = body["user"]["id"]
    ts = body["message"]["ts"]
    status = body["message"]["blocks"][2]["block_id"]
    (
        ban,
        teban_motigoma,
        unteban_motigoma,
        teban_user,
        unteban_user,
        last_sashite,
        tesu,
    ) = deconpress_status(status)

    if user == teban_user:
        respond(
            blocks=generate_ephemeral_block(ts, status),
            replace_original=False,
        )
    else:
        respond(f"<@{teban_user}> の手番です", replace_original=False)


def lose(respond, body, client):
    channel = body["channel"]["id"]
    user = body["user"]["id"]
    block_id = body["actions"][0]["block_id"]
    ts = block_id.split(":")[0]
    status = block_id.split(":")[1]

    respond("処理中...")

    (
        ban,
        teban_motigoma,
        unteban_motigoma,
        teban_user,
        unteban_user,
        last_sashite,
        tesu,
    ) = deconpress_status(status)

    if user == teban_user:
        generate_board_image(
            user, ts, ban, teban_motigoma, unteban_motigoma, 8 - np.array(last_sashite)
        )
        url = put_s3_and_get_url(user, ts)
        client.chat_update(
            channel=channel,
            ts=ts,
            blocks=generate_board_block(
                url, status, teban_user, tesu, is_end=True, winner=unteban_user
            ),
            text=f"{tesu}手目",
        )
        respond("あなたの負けです。お疲れ様でした。")
    else:
        respond(f"<@{teban_user}> の手番です", replace_original=False)


def show(body, client):
    channel = body["channel"]["id"]
    user = body["user"]["id"]
    ts = body["message"]["ts"]
    status = body["message"]["blocks"][2]["block_id"]
    is_end = body["message"]["blocks"][2]["type"] == "section"

    (
        ban,
        teban_motigoma,
        unteban_motigoma,
        teban_user,
        unteban_user,
        last_sashite,
        tesu,
    ) = deconpress_status(status)

    generate_board_image(
        user, ts, ban, teban_motigoma, unteban_motigoma, 8 - np.array(last_sashite)
    )
    url = put_s3_and_get_url(user, ts)
    client.chat_update(
        channel=channel,
        ts=ts,
        blocks=generate_board_block(
            url, status, teban_user, tesu, is_end=is_end, winner=unteban_user
        ),
        text=f"{tesu}手目",
    )


app.action("plain_text_input_update-action")(ack=arc_func, lazy=[update])
app.action("button_lose-action")(ack=arc_func, lazy=[lose])
app.action("button_lose_confirm-action")(ack=arc_func, lazy=[lose_confirm])
app.action("button_show-action")(ack=arc_func, lazy=[show])
