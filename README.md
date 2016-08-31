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

    // // total_fee 单位为分
    pay.jsapi(openid='openid', body='测试', out_trade_no='1', total_fee=1)

#### 检查响应数据

    pay.check(pay.to_dict(request.data))


### 微信消息

