# -*- coding: utf-8 -*-


from weixin import WeixinMP, WeixinError


app_id = ''
app_secret = ''
mp = WeixinMP(app_id, app_secret)

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

# 短连接
print mp.shorturl("http://baidu.com").short_url

# 创建带参数的零时qrcode, 30秒过期
data = mp.qrcode_create(123456, 30)
print mp.qrcode_show(data.ticket)

# 创建带参数永久性qrcode
data = mp.qrcode_create_limit(123456)
print mp.qrcode_show(data.ticket)
