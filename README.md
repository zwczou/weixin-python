微信SDK
======

提供微信登陆，公众号管理，微信支付，微信消息的全套功能

## 文档目录

* [快速开始](#目录)
* [微信消息](https://github.com/zwczou/weixin-python/wiki/%E5%BE%AE%E4%BF%A1%E6%B6%88%E6%81%AF)
* [微信支付](https://github.com/zwczou/weixin-python/wiki/%E5%BE%AE%E4%BF%A1%E6%94%AF%E4%BB%98)
* [微信登陆](https://github.com/zwczou/weixin-python/wiki/%E5%BE%AE%E4%BF%A1%E7%99%BB%E9%99%86)
* [微信公众平台](https://github.com/zwczou/weixin-python/wiki/%E5%BE%AE%E4%BF%A1%E5%85%AC%E4%BC%97%E5%B9%B3%E5%8F%B0)

欢迎提交[Pull requests](https://github.com/zwczou/weixin-python/pulls)


如果需要单独使用其中的某些模块，可以见[文档目录](#文档目录)的具体模块

如果需要组合在一起可以参考[快速开始](#目录)

## 目录

* [安装](#安装)
* [功能](#功能)
* [异常](#异常)
* [用法](#用法)
	* [参数](#参数)
	* [初始化](#初始化)
	* [微信消息](#微信消息)
	* [微信登陆](#微信登陆)
	* [微信支付](#微信支付)
	* [微信公众号](#微信公众号)

## 安装

使用pip

`sudo pip install weixin-python`

使用easy_install

`sudo easy_install weixin-python`

## 功能

* 微信登陆
* 微信支付
* 微信公众号
* 微信消息

## 异常

父异常类名为 `WeixinError`
子异常类名分别为 `WeixinLoginError` `WeixinPayError` `WeixinMPError` `WeixinMsgError`

## 用法

### 参数

* `WEIXIN_TOKEN` 必填，微信主动推送消息的TOKEN
* `WEIXIN_SENDER` 选填，微信发送消息的发送者
* `WEIXIN_EXPIRES_IN` 选填，微信推送消息的有效时间
* `WEIXIN_MCH_ID` 必填，微信商户ID，纯数字
* `WEIXIN_MCH_KEY` 必填，微信商户KEY
* `WEIXIN_NOTIFY_URL` 必填，微信回调地址
* `WEIXIN_MCH_KEY_FILE` 可选，如果需要用退款等需要证书的api，必选
* `WEIXIN_MCH_CERT_FILE` 可选
* `WEIXIN_APP_ID` 必填，微信公众号appid
* `WEIXIN_APP_SECRET` 必填，微信公众号appkey

上面参数的必填都是根据具体开启的功能有关, 如果你只需要微信登陆，就只要选择 `WEIXIN_APP_ID` `WEIXIN_APP_SECRET`

* 微信消息
   * `WEIXIN_TOKEN`
   * `WEIXIN_SENDER`
   * `WEIXIN_EXPIRES_IN`

* 微信登陆
    * `WEIXIN_APP_ID`
    * `WEIXIN_APP_SECRET`

* 微信公众平台
    * `WEIXIN_APP_ID`
    * `WEIXIN_APP_SECRET`

* 微信支付
    * `WEIXIN_APP_ID`
    * `WEIXIN_MCH_ID`
    * `WEIXIN_MCH_KEY`
    * `WEIXIN_NOTIFY_URL`
    * `WEIXIN_MCH_KEY_FILE`
    * `WEIXIN_MCH_CERT_FILE`

### 初始化

如果使用flask

```
# -*- coding: utf-8 -*-


from datetime import datetime, timedelta
from flask import Flask, jsonify, request, url_for
from weixin import Weixin, WeixinError


app = Flask(__name__)
app.debug = True


# 具体导入配
# 根据需求导入仅供参考
app.config.fromobject(dict(WEIXIN_APP_ID='', WEIXIN_APP_SECRET=''))


# 初始化微信
weixin = Weixin()
weixin.init_app(app)
# 或者
# weixin = Weixin(app)

```

如果不使用flask

```
# 根据需求导入仅供参考
config = dict(WEIXIN_APP_ID='', WEIXIN_APP_SECRET='')
weixin = Weixin(config)
```

### 微信消息

如果使用django，添加视图函数为

```
url(r'^/$', weixin.django_view_func(), name='index'),

```

如果为flask，添加视图函数为

```
app.add_url_rule("/", view_func=weixin.view_func)
```


```
@weixin.all
def all(**kwargs):
	"""
	监听所有没有更特殊的事件
	"""
    return weixin.reply(kwargs['sender'], sender=kwargs['receiver'], content='all')


@weixin.text()
def hello(**kwargs):
	"""
	监听所有文本消息
	"""
    return "hello too"


@weixin.text("help")
def world(**kwargs):
	"""
	监听help消息
	"""
    return dict(content="hello world!")


@weixin.subscribe
def subscribe(**kwargs):
	"""
	监听订阅消息
	"""
    print kwargs
    return "欢迎订阅我们的公众号"
````

# 微信登陆

````
@app.route("/login")
def login():
    """登陆跳转地址"""
	openid = request.cookies.get("openid")
    next = request.args.get("next") or request.referrer or "/",
    if openid:
        return redirect(next)

    callback = url_for("authorized", next=next, _external=True)
    url = weixin.authorize(callback, "snsapi_base")
    return redirect(url)


@app.route("/authorized")
def authorized():
	"""登陆回调函数"""
    code = request.args.get("code")
    if not code:
        return "ERR_INVALID_CODE", 400
    next = request.args.get("next", "/")
    data = weixin.access_token(code)
    openid = data.openid
    resp = redirect(next)
    expires = datetime.now() + timedelta(days=1)
    resp.set_cookie("openid", openid, expires=expires)
    return resp
```

# 微信支付

注意: 微信网页支付的timestamp参数必须为字符串

```


@app.route("/pay/jsapi")
def pay_jsapi():
	"""微信网页支付请求发起"""
	try:
        out_trade_no = weixin.nonce_str
        raw = weixin.jsapi(openid="openid", body=u"测试", out_trade_no=out_trade_no, total_fee=1)
        return jsonify(raw)
    except WeixinError, e:
        print e.message
        return e.message, 400


@app.route("/pay/notify")
def pay_notify():
    """
    微信异步通知
    """
    data = weixin.to_dict(request.data)
    if not weixin.check(data):
        return weixin.reply("签名验证失败", False)
    # 处理业务逻辑
    return weixin.reply("OK", True)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9900)
```

### 微信公众号

**注意**: 如果使用分布式，需要自己实现`access_token`跟`jsapi_ticket`函数

`access_token`默认保存在`~/.access_token`
`jsapi_ticket`默认保存在`~/.jsapi_ticket`

默认在(HOME)目录下面，如果需要更改到指定的目录，可以导入库之后修改，如下

```
import weixin

DEFAULT_DIR = "/tmp"
```

获取公众号唯一凭证

	weixin.access_token


获取ticket

	weixin.jsapi_ticket


创建临时qrcode

	data = weixin.qrcode_create(123, 30)
	print weixin.qrcode_show(data.ticket)

创建永久性qrcode

	# scene_id类型
	weixin.qrcode_create_limit(123)
	# scene_str类型
	weixin.qrcode_create_limit("456")

长链接变短链接

	weixin.shorturl("http://example.com/test")
