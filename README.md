微信SDK
======

提供微信登陆，公众号管理，微信支付，微信消息等处理

## 安装

    pip install weixin-python


## 用法

### 微信登陆

    from weixin.login import WeixinLogin

    login = WeixinLogin(app_id, app_secret)

#### 生成认证地址

    url = login.authorize("http://example.com/authorized", "snsapi_base")

#### 获取用户信息

    data = login.access_token(code)
    user_info = login.user_info(data.access_token, data.openid)
    print user_info.nickname
    print usre_info.name

### 公众号管理

#### 创建qrcode

#### 长链接变短链接

#### 菜单管理

#### 关注列表

### 微信支付

    from weixin.pay import WeixinPay

    pay = WeixinPay(app_id, mch_id, mch_key, notify_url)

#### 生成JSSDK需要的参数

    # total_fee 单位为分
    pay.jsapi(openid='openid', body='测试', out_trade_no='1', total_fee=1)

#### 检查响应数据

    pay.check(pay.to_dict(request.data))


### 微信消息


首先初始化

    from flask import Flask
    from weixin.msg import WeixinMsg

    app = Flask(__name__)
    msg = WeixinMsg("e10adc3949ba59abbe56e057f20f883e", None, 0)

如果使用flask建议使用默认视图函数

    app.add_url_rule("/", view_func=msg.view_func)

    @msg.all
    def all_test(**kwargs):
        return msg.reply(
            kwargs['sender'], sender=kwargs['receiver'], content='all'
        )

上面例子可以接收所有的用户发送的消息, 如果需要更加特殊的

    @msg.text("hello")
    def hello(**kwargs):
        return msg.reply(
            kwargs['sender'], sender=kwargs['receiver'], content='hello too'
        )

这个函数将处理用户发送的文本消息并且内容为 `hello`

还有更多消息内容包装器

    * 图片类型 `@msg.image`
    * 视频类型 `@msg.video` `@msg.shortvideo`
    * 音频类型 `@msg.voice`
    * 坐标类型 `@msg.location`
    * 链接类型 `@msg.link`

还可以监听事件

    * 订阅事件 `@msg.subscribe`
    * 取消订阅事件 `@msg.unsubscribe`
    * 点击事件 `@msg.click`
    * 其它事件 `@msg.{event}`

具体使用方式可以参考 `example/msg.py`
