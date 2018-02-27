微信消息
========

来源
----

本模块主要代码来源于\ `lepture/flask-weixin`_

功能
----

-  接收微信推送消息
-  接受微信推送事件
-  发送微信消息

文档
----

微信详细文档\ `请点击`_

初始化
~~~~~~

::

    from weixin import WeixinMsg
    # from weixin.msg import WeixinMsg

    msg = WeixinMsg('token')

    # 如果使用flask
    app.add_url_rule("/", view_func=msg.view_func)

    # 如果使用django
    # url(r'^/$', msg.django_view_func(), name='index')

接收消息
~~~~~~~~

微信推送消息过来的时候，会先寻找最特殊的规则，然后再是普片的

监听所有
^^^^^^^^

支持的消息类型
^^^^^^^^^^^^^^

-  所有类型 ``@msg.all``
-  文本类型 ``@msg.text()`` ``@msg.text("help")``
-  图片类型 ``@msg.image``
-  视频类型 ``@msg.video`` ``@msg.shortvideo``
-  音频类型 ``@msg.voice``
-  坐标类型 ``@msg.location``
-  链接类型 ``@msg.link``
-  事件类型 ``@msg.event``

::

    @msg.all
    def all(**kwargs):
        return "所有事件"

监听文本消息
^^^^^^^^^^^^

::

    @msg.text()
    def text(**kwargs):
        return "所有文本消息"

监听具体的文本消息
^^^^^^^^^^^^^^^^^^

::

    @msg.text("help")
    def help(**kwargs):
        return "可以通过4001000联系我们"

监听图片消息
^^^^^^^^^^^^

::

    @msg.image
    def image():
        return dict(content="image")

监听事件
~~~~~~~~

支持的事件类型
^^^^^^^^^^^^^^

-  订阅事件 ``@msg.subscribe``
-  取消订阅事件 ``@msg.unsubscribe``
-  点击事件 ``@msg.click``
-  其它事件 ``@msg.{event}``

监听订阅事件
^^^^^^^^^^^^

::

    @msg.subscribe
    def subscribe():
        return "欢迎关注我的公众号code_show"

监听取消订阅事件
^^^^^^^^^^^^^^^^

::

    @msg.unsubscribe
    def unsubscribe():
        return ""

监听点击事件
~~~~~~~~~~~~

::

    @msg.click
    def click(**kwargs):
        print kwargs
        return ""

发送消息
~~~~~~~~

支持回复消息的类型
^^^^^^^^^^^^^^^^^^

-  文本消息 ``text``
-  音乐消息 ``music``
-  视频消息 ``video``
-  音频消息 ``voice``
-  图片消息 ``image``
-  新闻消息 ``news``

直接在函数里面回复字符串
^^^^^^^^^^^^^^^^^^^^^^^^

默认类型为文本消息

::

    @msg.click
    def click(**kwargs):
        return "欢迎点击"

回复字典类型的消息
^^^^^^^^^^^^^^^^^^

会自动填充发送者跟接受者

::

    @msg.click
    def click():
        return dict(content="欢迎点击", type="text")

使用\ ``reply``\ 函数
^^^^^^^^^^^^^^^^^^^^^

::

    @msg.click
    def click(**kwargs):
        return msg.reply(kwargs['sender'], sender=kwargs['receiver'], content='click')

用法
~~~~

::

    # -*- coding: utf-8 -*-


    from flask import Flask
    from weixin.msg import WeixinMsg


    app = Flask(__name__)
    msg = WeixinMsg("e10adc3949ba59abbe56e057f20f883e", None, 0)


    app.add_url_rule("/", view_func=msg.view_func)


    @msg.all
    def all_test(**kwargs):
        print kwargs
        # 或者直接返回
        # return "all"
        return msg.reply(
            kwargs['sender'], sender=kwargs['receiver'], content='all'
        )


    @msg.text()
    def hello(**kwargs):
        return dict(content="hello too!", type="text")


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

.. _lepture/flask-weixin: https://github.com/lepture/flask-weixin
.. _请点击: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421140453&token=&lang=zh_CN
