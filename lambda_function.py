import os
import re
import numpy as np
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

from s3 import put_s3_and_get_url
from exceptions import ParseInputBaseError, ShogiBaseError
from slack_components import (
    generate_board,
    generate_block,
    compress_status,
    deconpress_status,
)
from parse_input import ParseInput
from shogi import Shogi

# Initializes your app with your bot token and signing secret
app = App(
    process_before_response=True,
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)


def lambda_handler(event, context):
    # 再送防止
    if event["headers"].get("X-Slack-Retry-Num", False):
        return {"statusCode": 200, "body": "no need retry"}
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)


########################################################################
def update_board(body, respond, say, client):
    channel = body["channel"]["id"]
    ts = body["message"]["ts"]

    print(body)
    kishi = "<@" + body["user"]["id"] + ">"
    status = list(body["state"]["values"].keys())[0]
    print(status)

    sashite = body["state"]["values"][status]["plain_text_input-action"]["value"]
    (
        ban,
        teban_motigoma,
        unteban_motigoma,
        teban,
        unteban,
        last_sashite,
        tesu,
    ) = deconpress_status(status)

    if kishi == teban:
        try:
            parseinput = ParseInput()
            sashite_ = parseinput.parse(sashite, last_sashite)
        except ParseInputBaseError as e:
            respond(str(e), replace_original=False)
        else:
            shogi = Shogi(ban, teban_motigoma, unteban_motigoma)
            try:
                shogi.action(*sashite_)
            except ShogiBaseError as e:
                respond(str(e), replace_original=False)
            else:
                teban, unteban = unteban, teban
                ban = shogi.board.tolist()
                teban_motigoma = shogi.teban_motigoma
                unteban_motigoma = shogi.unteban_motigoma

                generate_board(ban, teban_motigoma, unteban_motigoma, sashite_)
                url = put_s3_and_get_url()
                status = compress_status(
                    ban,
                    teban_motigoma,
                    unteban_motigoma,
                    teban,
                    unteban,
                    sashite_,
                    tesu,
                )
                print(sashite_)
                client.chat_update(
                    channel=channel,
                    ts=ts,
                    blocks=generate_block(url, status, teban, sashite, tesu),
                    text=f"{tesu}手目 {sashite}",
                )
    else:
        respond(f"{teban}の手番です", replace_original=False)


def arc_func(ack):
    ack()


app.action("plain_text_input-action")(ack=arc_func, lazy=[update_board])


@app.event("app_mention")
def say_hello(message, say, body, ack, client):
    channel = body["event"]["channel"]
    message = body["event"]["text"]
    opponent = re.findall(r"<@[A-Z0-9]{9}>", message)
    if len(opponent) != 1:
        say("対戦相手を一人選んでメンションしてください", replace_original=False)
    else:
        user_dict = {0: "<@" + body["event"]["user"] + ">", 1: opponent[0]}

        hurigoma = int((np.random.random() * 2 // 1))
        teban = user_dict[hurigoma]
        unteban = user_dict[hurigoma ^ 1]
        say(channel=channel, text=f"{teban}が先手じゃ！")
        say(channel=channel, text=f"{unteban}が後手じゃ！")

        ack()

        shogi = Shogi()
        ban = shogi.board.tolist()
        teban_motigoma = shogi.teban_motigoma
        unteban_motigoma = shogi.unteban_motigoma

        generate_board(ban)  # 画像作成
        url = put_s3_and_get_url()
        status = compress_status(ban, teban_motigoma, unteban_motigoma, teban, unteban)

        say(channel=channel, text="text", blocks=generate_block(url, status, teban))


#################################################################
