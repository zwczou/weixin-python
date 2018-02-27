微信公众平台
============

文档
----

初始化
~~~~~~

::

    from weixin.mp import WeixinMP

    mp = WeixinMP(app_id, app_secret)

获取公众号唯一凭证
~~~~~~~~~~~~~~~~~~

::

    print mp.access_token

获取jsticket
~~~~~~~~~~~~

::

    print mp.jsapi_ticket

jsapi签名，比如扫码或者分享
~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    mp.jsapi_sign(url=request.url)

创建临时qrcode
~~~~~~~~~~~~~~

::

    data = mp.qrcode_create(123, 30)
    print mp.qrcode_show(data.ticket)

创建永久性qrcode
~~~~~~~~~~~~~~~~

::

    # scene_id类型
    mp.qrcode_create_limit(123)
    # scene_str类型
    mp.qrcode_create_limit("456")

长链接变短链接
~~~~~~~~~~~~~~

::

    mp.shorturl("http://example.com/test")

菜单管理
~~~~~~~~

::

    # 获取菜单
    try:
        print mp.menu_get()
    except WeixinError:
        pass

    # 创建菜单
    data = [
        {
            "type": "view",
            "name": "测试",
            "url": "http://code.show/",
        },
    ]
    print mp.menu_create(data)

    # 删除菜单
    print mp.menu_delete()

    # 模板消息
    print mp.get_all_private_template()
    print mp.del_private_template("oHmefUCu3hUa1r23iun2gP3BM9MVn11g7Ob2J4VzpOg")

    data = {
        "first": {
            "value":u"恭喜你购买成功！",
            "color":"#173177"
        },
        "accountType":{
            "value":u"巧克力",
            "color":"#173177"
        },
        "account": {
            "value":u"39.8元",
            "color":"#173177"
        },
        "amount": {
            "value":u"2014年9月22日",
            "color":"#173177"
        },
        "result": {
            "value":u"2014年9月22日",
            "color":"#173177"
        },
        "remark":{
            "value":u"欢迎再次购买\nabc\nefg",
            "color":"#173177"
        }
    }

    print mp.template_send("oHmefUCu3hUa1r23iun2gP3BM9MVn11g7Ob2J4VzpOg", "oYhHdsswUDolWKEbeybuA0sHr5W4", data)

更多用法参考 `example/mp.py`_

TODO
~~~~

-  [X] 自定义菜单
-  [X] 用户管理

   -  [X] 用户分组管理
   -  [X] 设置用户备注名
   -  [X] 获取用户基本信息
   -  [X] 获取用户列表
   -  [X] 获取用户地理位置

-  [X] 账号管理

   -  [X] 生成带参数的二维码
   -  [X] 长链接转短链接
   -  [X] 微信认证事件推送

-  [X] 消息管理

   -  [X] 普通消息 `微信消息`_
   -  [X] 模板消息

-  [ ] 素材管理

.. _example/mp.py: https://github.com/zwczou/weixin-python/blob/master/example/mp.py
.. _微信消息: https://github.com/zwczou/weixin-python/wiki/微信消息
