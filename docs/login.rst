微信登陆
========

功能
----

-  支持snsapi_base,
   以snsapi_base为scope发起的网页授权，是用来获取进入页面的用户的openid的，并且是静默授权并自动跳转到回调页的。用户感知的就是直接进入了回调页（往往是业务页面）
-  支持snsapi_userinfo,
   以snsapi_userinfo为scope发起的网页授权，是用来获取用户的基本信息的。但这种授权需要用户手动同意，并且由于用户同意过，所以无须关注，就可在授权后获取该用户的基本信息。

文档
----

微信详细文档\ `请点击`_

初始化
~~~~~~

::

    from weixin import WeixinLogin
    # from weixin.login import WeixinLogin

    login = WeixinLogin('app_id', 'app_key')

引导用户跳转到授权页面
~~~~~~~~~~~~~~~~~~~~~~

::

    url = login.authorize("http://code.show/login/weixin/callback", "snsapi_base")

通过code换取网页授权access_token
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    data = login.access_token(code)
    print data.access_token
    print data.refresh_token
    print data.openid


小程序通过js_code换取session跟openid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    data = login.jscode2session(code)


拉取用户信息
~~~~~~~~~~~~

如果是snsapi_userinfo则需要

::

    login.user_info(data.access_token)

刷新token
~~~~~~~~~

::

    login.refresh_token(data.refresh_token)

用法
----

::

    # -*- coding: utf-8 -*-


    from datetime import datetime, timedelta
    from flask import Flask, redirect, request, url_for
    from weixin.login import WeixinLogin


    app = Flask(__name__)

    app_id = ''
    app_secret = ''
    wx_login = WeixinLogin(app_id, app_secret)


    @app.route("/login")
    def login():
        openid = request.cookies.get("openid")
        next = request.args.get("next") or request.referrer or "/",
        if openid:
            return redirect(next)

        callback = url_for("authorized", next=next, _external=True)
        url = wx_login.authorize(callback, "snsapi_base")
        return redirect(url)


    @app.route("/authorized")
    def authorized():
        code = request.args.get("code")
        if not code:
            return "ERR_INVALID_CODE", 400
        next = request.args.get("next", "/")
        data = wx_login.access_token(code)
        openid = data.openid
        resp = redirect(next)
        expires = datetime.now() + timedelta(days=1)
        resp.set_cookie("openid", openid, expires=expires)
        return resp

.. _请点击: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421140842&token=&lang=zh_CN
