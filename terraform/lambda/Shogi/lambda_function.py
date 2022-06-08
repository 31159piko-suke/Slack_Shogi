import os
import re
import numpy as np
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from slack_bolt.adapter.aws_lambda.lambda_s3_oauth_flow import LambdaS3OAuthFlow

from s3 import put_s3_and_get_url
from dynamoDB import register_user
from exceptions import InputBaseError, ShogiBaseError
from slack_components import (
    generate_board_image,
    generate_board_block,
    generate_ephemeral_block,
    compress_status,
    deconpress_status,
)
from input import Input
from shogi import Shogi

app = App(
    process_before_response=True,
    oauth_flow=LambdaS3OAuthFlow(),
)


def lambda_handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)


@app.use
def no_retry(context, ack, next):
    if (
        context.get("lambda_request", {})
        .get("headers", {})
        .get("x-slack-retry-num", False)
    ):
        ack()
        return 200
    else:
        next()


@app.event("app_mention")
def start_game(ack, say, body, client, logger):
    logger.info(body)
    ack()
    channel = body["event"]["channel"]
    user = body["event"]["user"]
    ts = body["event"]["ts"]

    message = body["event"]["text"]
    opponents_list = re.findall(r"<@[A-Z0-9]{9,11}>", message)
    if len(opponents_list) != 2:
        say("対戦相手を一人選んでメンションしてください", replace_original=False)
    else:
        try:
            is_bot_0 = (
                client.users_info(user=opponents_list[0][2:-1])
                .get("user", {})
                .get("is_bot", True)
            )
            is_bot_1 = (
                client.users_info(user=opponents_list[1][2:-1])
                .get("user", {})
                .get("is_bot", True)
            )

            if not is_bot_0:
                opponent = opponents_list[0]
            elif not is_bot_1:
                opponent = opponents_list[1]

            user_dict = {0: user, 1: opponent[2:-1]}

            hurigoma = int((np.random.random() * 2 // 1))
            teban_user = user_dict[hurigoma]
            unteban_user = user_dict[hurigoma ^ 1]
            register_user(teban_user)
            register_user(unteban_user)
        except:
            say("対戦相手を一人選んでメンションしてください", replace_original=False)
        else:
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
                blocks=generate_board_block(
                    teban_user, unteban_user, url, status, teban_user
                ),
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
            input = Input()
            parsed_sashite = input.parse(
                sashite, [8 - int(i) for i in last_sashite[:2]]
            )
            formated_sashite = input.format(parsed_sashite, tesu)
        except InputBaseError as e:
            respond(str(e), replace_original=False)
        else:
            shogi = Shogi(ban, teban_motigoma, unteban_motigoma)
            try:
                shogi.action(*parsed_sashite)
                tesu += 1
            except ShogiBaseError as e:
                respond(str(e), replace_original=False)
            else:
                teban_user, unteban_user = unteban_user, teban_user
                ban = shogi.board.tolist()
                teban_motigoma = shogi.teban_motigoma
                unteban_motigoma = shogi.unteban_motigoma

                generate_board_image(
                    user, ts, ban, teban_motigoma, unteban_motigoma, parsed_sashite
                )
                url = put_s3_and_get_url(user, ts)
                status = compress_status(
                    ban,
                    teban_motigoma,
                    unteban_motigoma,
                    teban_user,
                    unteban_user,
                    parsed_sashite,
                    tesu,
                )
                client.chat_update(
                    channel=channel,
                    ts=ts,
                    blocks=generate_board_block(
                        unteban_user,
                        teban_user,
                        url,
                        status,
                        teban_user,
                        tesu=tesu,
                        sashite=formated_sashite,
                    ),
                    text=f"{tesu}手目 {formated_sashite}",
                )
                client.chat_postMessage(
                    channel=channel, thread_ts=ts, text=f"{tesu}手目 {formated_sashite}"
                )
    else:
        respond(f"<@{teban_user}> の手番です", replace_original=False)


def lose_confirm(respond, body):
    user = body["user"]["id"]
    ts = body["message"]["ts"]
    status = body["message"]["blocks"][3]["block_id"]
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

    input = Input()
    formated_sashite = input.format(last_sashite, tesu)

    if user == teban_user:
        generate_board_image(
            user,
            ts,
            ban,
            teban_motigoma,
            unteban_motigoma,
            sashite=[int(i) for i in last_sashite[:2]],
        )
        url = put_s3_and_get_url(user, ts)
        client.chat_update(
            channel=channel,
            ts=ts,
            blocks=generate_board_block(
                teban_user,
                unteban_user,
                url,
                status,
                teban_user,
                tesu=tesu,
                sashite=formated_sashite,
                is_end=True,
                winner=unteban_user,
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
    status = body["message"]["blocks"][3]["block_id"]
    is_end = body["message"]["blocks"][3]["type"] == "section"

    (
        ban,
        teban_motigoma,
        unteban_motigoma,
        teban_user,
        unteban_user,
        last_sashite,
        tesu,
    ) = deconpress_status(status)

    input = Input()
    formated_sashite = input.format(last_sashite, tesu)

    generate_board_image(
        user,
        ts,
        ban,
        teban_motigoma,
        unteban_motigoma,
        sashite=[int(i) for i in last_sashite[:2]],
    )
    url = put_s3_and_get_url(user, ts)
    client.chat_update(
        channel=channel,
        ts=ts,
        blocks=generate_board_block(
            teban_user,
            unteban_user,
            url,
            status,
            teban_user,
            tesu=tesu,
            sashite=formated_sashite,
            is_end=is_end,
            winner=unteban_user,
        ),
        text=f"{tesu}手目",
    )


app.action("plain_text_input_update-action")(ack=arc_func, lazy=[update])
app.action("button_lose-action")(ack=arc_func, lazy=[lose])
app.action("button_lose_confirm-action")(ack=arc_func, lazy=[lose_confirm])
app.action("button_show-action")(ack=arc_func, lazy=[show])
