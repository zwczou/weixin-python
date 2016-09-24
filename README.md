微信SDK
======

提供微信登陆，公众号管理，微信支付，微信消息等处理

### 目录

* [安装](#安装)
* [快速开始](https://github.com/zwczou/weixin-python/wiki/%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B)
* [微信消息](https://github.com/zwczou/weixin-python/wiki/%E5%BE%AE%E4%BF%A1%E6%B6%88%E6%81%AF)
* [微信支付](https://github.com/zwczou/weixin-python/wiki/%E5%BE%AE%E4%BF%A1%E6%94%AF%E4%BB%98)
* [微信登陆](#微信登陆)
* [公众号相关](#公众号管理)
    * [TODO](#todo)
* [更多文档](https://github.com/zwczou/weixin-python/wiki)


## 安装

    pip install weixin-python


## 微信登陆

初始化

    from weixin.login import WeixinLogin

    login = WeixinLogin(app_id, app_secret)

微信有两种scope

1. snsapi_base 只能获取用户的openid，不需要用户确认
2. snsapi_userinfo 可以获取用户信息，需要用户主动确认


snsapi_base方式

    url = login.authorize("http://example.com/authorized", "snsapi_base")

snsapi_usrinfo方式

    url = login.authorize("http://example.com/authorized", "snsapi_userinfo")

获取用户信息

    # 首根据code获取access_token跟openid
    data = login.access_token(code)
    # 如果scope为`snsapi_userinfo`可以执行以下操作
    user_info = login.user_info(data.access_token, data.openid)
    print user_info.nickname
    print usre_info.name

更多用法可以参考 [example/login.py](https://github.com/zwczou/weixin-python/blob/master/example/login.py)

## 公众号管理

初始化

    from weixin.mp import WeixinMP

    mp = WeixinMP(app_id, app_secret)

获取公众号唯一凭证

    print mp.access_token

创建临时qrcode

    data = mp.qrcode_create(123, 30)
    print mp.qrcode_show(data.ticket)

创建永久性qrcode

    # scene_id类型
    mp.qrcode_create_limit(123)
    # scene_str类型
    mp.qrcode_create_limit("456")

长链接变短链接

    mp.shorturl("http://example.com/test")

菜单管理

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

更多用法参考 [example/mp.py](https://github.com/zwczou/weixin-python/blob/master/example/mp.py)

### TODO

* [X] 自定义菜单
* [X] 用户管理
    * [X] 用户分组管理
    * [X] 设置用户备注名
    * [X] 获取用户基本信息
    * [X] 获取用户列表
    * [X] 获取用户地理位置
* [X] 账号管理
    * [X] 生成带参数的二维码
    * [X] 长链接转短链接
    * [X] 微信认证事件推送
* [X] 消息管理
    * [X] 普通消息 [微信消息](#微信消息)
    * [ ] 模板消息
* [ ] 素材管理
