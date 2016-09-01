# -*- coding: utf-8 -*-


from flask import current_app

from msg import WeixinMsg
from pay import WeixinPay
from login import WeixinLogin
from mp import WeixinMP
from base import WeixinError, Map


class Weixin(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
            self.app = app

    def init_app(self, app):
        token = app.config.get("WEIXIN_TOKEN")
        sender = app.config.get('WEIXIN_SENDER', None)
        expires_in = app.config.get('WEIXIN_EXPIRES_IN', 0)
        mch_id = app.config.get("WEIXIN_MCH_ID")
        mch_key = app.config.get("WEIXIN_MCH_KEY")
        notify_url = app.config.get("WEIXIN_NOTIFY_URL")
        app_id = app.config.get("WEIXIN_APP_ID")
        app_secret = app.config.get("WEIXIN_APP_SECRET")
        if token:
            self.msg = WeixinMsg(token, sender, expires_in)
        if app_id and mch_id and mch_key and notify_url:
            self.pay = WeixinPay(app_id, mch_id, mch_key, notify_url)
        if app_id and app_secret:
            self.login = WeixinLogin(app_id, app_secret)
            self.mp = WeixinMP(app_id, app_secret)
