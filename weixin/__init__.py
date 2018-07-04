# -*- coding: utf-8 -*-


from .msg import WeixinMsg
from .pay import WeixinPay
from .login import WeixinLogin
from .mp import WeixinMP
from .base import WeixinError, Map

from collections import namedtuple


__all__ = ("Weixin")
__author__ = "Weicheng Zou <zwczou@gmail.com>"
__version__ = "0.5.4"


StandaloneApplication = namedtuple("StandaloneApplication", ["config"])


class Weixin(WeixinLogin, WeixinPay, WeixinMP, WeixinMsg):
    """
    微信SDK

    :param app 如果非flask，传入字典配置，如果是flask直接传入app实例
    """
    def __init__(self, app=None):
        if app is not None:
            if isinstance(app, dict):
                app = StandaloneApplication(config=app)
            self.init_app(app)
            self.app = app

    def init_app(self, app):
        if isinstance(app, dict):
            app = StandaloneApplication(config=app)

        token = app.config.get("WEIXIN_TOKEN")
        sender = app.config.get('WEIXIN_SENDER', None)
        expires_in = app.config.get('WEIXIN_EXPIRES_IN', 0)
        mch_id = app.config.get("WEIXIN_MCH_ID")
        mch_key = app.config.get("WEIXIN_MCH_KEY")
        notify_url = app.config.get("WEIXIN_NOTIFY_URL")
        mch_key_file = app.config.get("WEIXIN_MCH_KEY_FILE")
        mch_cert_file = app.config.get("WEIXIN_MCH_CERT_FILE")
        app_id = app.config.get("WEIXIN_APP_ID")
        app_secret = app.config.get("WEIXIN_APP_SECRET")
        if token:
            WeixinMsg.__init__(self, token, sender, expires_in)
        if app_id and mch_id and mch_key and notify_url:
            WeixinPay.__init__(self, app_id, mch_id, mch_key, notify_url, mch_key_file, mch_cert_file)
        if app_id and app_secret:
            WeixinLogin.__init__(self, app_id, app_secret)
            WeixinMP.__init__(self, app_id, app_secret)

        # 兼容老版本
        if app_id and mch_id and mch_key and notify_url:
            self.pay = WeixinPay(app_id, mch_id, mch_key, notify_url, mch_key_file, mch_cert_file)
        if token:
            self.msg = WeixinMsg(token, sender, expires_in)
        if app_id and app_secret:
            self.login = WeixinLogin(app_id, app_secret)
            self.mp = WeixinMP(app_id, app_secret)
