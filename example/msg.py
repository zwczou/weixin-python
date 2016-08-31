# -*- coding: utf-8 -*-


from flask import Flask
from weixin.msg import WeixinMsg


app = Flask(__name__)
msg = WeixinMsg("e10adc3949ba59abbe56e057f20f883e", None, 0)


app.add_url_rule("/", view_func=msg.view_func)


@msg.all
def all_test(**kwargs):
    print kwargs
    return msg.reply(
        kwargs['sender'], sender=kwargs['receiver'], content='all'
    )


@msg.text()
def hello(**kwargs):
    return msg.reply(
        kwargs['sender'], sender=kwargs['receiver'], content='hello too'
    )


@msg.text("world")
def world(**kwargs):
    return msg.reply(
        kwargs['sender'], sender=kwargs['receiver'], content='hello world!'
    )


@msg.image
def image(**kwargs):
    print kwargs
    return ""


@msg.subscribe
def subscribe(**kwargs):
    print kwargs
    return ""


@msg.unsubscribe
def unsubscribe(**kwargs):
    print kwargs
    return ""


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9900)
