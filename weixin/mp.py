# -*- coding: utf-8 -*-


from __future__ import unicode_literals

import os
import time
import json
import hashlib
import string
import random
import requests

from .base import Map, WeixinError


__all__ = ("WeixinMPError", "WeixinMP")


DEFAULT_DIR = os.getenv("HOME", os.getcwd())


class WeixinMPError(WeixinError):

    def __init__(self, msg):
        super(WeixinMPError, self).__init__(msg)


class WeixinMP(object):
    """
    微信公众号相关接口

    当需要全局使用access token可以选择继承WeixinMP实现access_token

        class WeixinMPSub(object):

            def __init__(self, app_id, app_secret):
                WeixinMP.__init__(app_id, app_secret)

            @property
            def access_token(self):
                return requests.get("http://example.com").content


        mp = WeixinMPSub("app_id", "app_secret")

    也可以选择传入jt_callback

        def get_access_token(mp):
            return requests.get("http://example.com").content

        WeixinMP("app_id", "app_secret", ac_callback=get_access_token)
    """

    api_uri = "https://api.weixin.qq.com"

    def __init__(self, app_id, app_secret, ac_path=None, jt_path=None, ac_callback=None, jt_callback=None):
        """
        :param :app_id 微信app id
        :param :app_secret 微信app secret
        :param :ac_path access token 保存路径
        :param :jt_path js ticket 保存路径
        :param :ac_callback ac_callback
        :param :jt_callback jt_callback
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.session = requests.Session()
        if ac_path is None:
            ac_path = os.path.join(DEFAULT_DIR, ".access_token")
        if jt_path is None:
            jt_path = os.path.join(DEFAULT_DIR, ".jsapi_ticket")
        self.ac_path = ac_path
        self.jt_path = jt_path
        self.ac_callback = ac_callback
        self.jt_callback = jt_callback

    def fetch(self, method, url, params=None, data=None, headers=None):
        req = requests.Request(method, url, params=params,
                               data=data, headers=headers)
        prepped = req.prepare()
        resp = self.session.send(prepped, timeout=20)
        data = Map(resp.json())
        if data.errcode:
            msg = "%(errcode)d %(errmsg)s" % data
            raise WeixinMPError(msg)
        return data

    def get(self, path, params=None, token=True, prefix="/cgi-bin"):
        url = "{0}{1}{2}".format(self.api_uri, prefix, path)
        params = {} if not params else params
        token and params.setdefault("access_token", self.access_token)
        return self.fetch("GET", url, params)

    def post(self, path, data, prefix="/cgi-bin", json_encode=True, token=True):
        url = "{0}{1}{2}".format(self.api_uri, prefix, path)
        params = {}
        token and params.setdefault("access_token", self.access_token)
        headers = {}
        if json_encode:
            # data = json.dumps(data, ensure_ascii=False)
            data = json.dumps(data)
            headers["Content-Type"] = "application/json;charset=UTF-8"
        # print url, params, headers, data
        return self.fetch("POST", url, params=params, data=data, headers=headers)

    @property
    def access_token(self):
        """
        获取服务端凭证

        当多台服务器需要共用access_token的时候
        如果不想自己继承实现access_token，可以传入ac_callback()
        接收一个WeixinMP对象作为参数
        """
        if self.ac_callback and callable(self.ac_callback):
            return self.ac_callback(self)

        timestamp = time.time()
        if not os.path.exists(self.ac_path) or \
                int(os.path.getmtime(self.ac_path)) < timestamp:
            params = dict()
            params.setdefault("grant_type", "client_credential")
            params.setdefault("appid", self.app_id)
            params.setdefault("secret", self.app_secret)
            data = self.get("/token", params, False)
            with open(self.ac_path, 'wb') as fp:
                fp.write(data.access_token.encode("utf-8"))
            os.utime(self.ac_path, (timestamp, timestamp + data.expires_in - 600))
        return open(self.ac_path).read().strip()

    @property
    def jsapi_ticket(self):
        """
        获取jsapi ticket

        当多台服务器需要共用js_ticket的时候
        如果不想自己继承实现js_ticket，可以传入jt_callback()
        接收一个WeixinMP对象作为参数
        """
        if self.jt_callback and callable(self.jt_callback):
            return self.jt_callback(self)

        timestamp = time.time()
        if not os.path.exists(self.jt_path) or \
                int(os.path.getmtime(self.jt_path)) < timestamp:
            params = dict()
            params.setdefault("type", "jsapi")
            data = self.get("/ticket/getticket", params, True)
            with open(self.jt_path, 'wb') as fp:
                fp.write(data.ticket.encode("utf-8"))
            os.utime(self.jt_path, (timestamp, timestamp + data.expires_in - 600))
        return open(self.jt_path).read()

    @property
    def nonce_str(self):
        char = string.ascii_letters + string.digits
        return "".join(random.choice(char) for _ in range(32))

    def jsapi_sign(self, **kwargs):
        """
        生成签名给js使用
        """
        timestamp = str(int(time.time()))
        nonce_str = self.nonce_str
        kwargs.setdefault("jsapi_ticket", self.jsapi_ticket)
        kwargs.setdefault("timestamp", timestamp)
        kwargs.setdefault("noncestr", nonce_str)
        raw = [(k, kwargs[k]) for k in sorted(kwargs.keys())]
        s = "&".join("=".join(kv) for kv in raw if kv[1])
        sign = hashlib.sha1(s.encode("utf-8")).hexdigest().lower()
        return Map(sign=sign, timestamp=timestamp, noncestr=nonce_str, appId=self.app_id)

    def groups_create(self, name):
        """
        创建分组

        :param name: 分组名
        """
        data = dict(group=dict(name=name))
        return self.post("/groups/create", data)

    def groups_get(self):
        """
        获取所有分组
        """
        return self.get("/groups/get")

    def groups_getid(self, openid):
        """
        查询用户所在分组

        :param openid: 用户id
        """
        data = dict(openid=openid)
        return self.post("/groups/getid", data)

    def groups_update(self, id, name):
        """
        修改分组名

        :param id: 分组id
        :param name: 分组名
        """
        data = dict(group=dict(id=id, name=name))
        return self.post("/groups/update", data)

    def groups_members_update(self, to_groupid, openid):
        """
        移动用户分组

        :param to_groupid: 分组id
        :param openid: 用户唯一标识符
        """
        data = dict(openid=openid, to_groupid=to_groupid)
        return self.post("/groups/members/update", data)

    def groups_members_batchupdate(self, to_groupid, *openid):
        """
        批量移动用户分组

        :param to_groupid: 分组id
        :param openid: 用户唯一标示列表
        """
        data = dict(openid_list=openid, to_groupid=to_groupid)
        return self.post("/groups/members/batchupdate", data)

    def groups_delete(self, id):
        """
        删除组

        :param id: 分组的id
        """
        data = dict(group=dict(id=id))
        return self.post("/groups/delete", data)

    def user_info_updateremark(self, openid, remark):
        """
        设置备注名

        :param openid: 用户唯一标识符
        :param remark: 备注
        """
        data = dict(openid=openid, remark=remark)
        return self.post("/user/info/updateremark", data)

    def user_info(self, openid):
        """
        获取用户信息
        包含subscribe字段，可以用来判断用户是否关注公众号

        :param openid: 用户id
        """
        args = dict(openid=openid, lang="zh_CN")
        return self.get("/user/info", args)

    def user_info_batchget(self, *openid):
        """
        批量获取用户信息
        """
        user_list = []
        for id in openid:
            user_list.append(dict(openid=openid, lang="zh_CN"))
        data = dict(user_list=user_list)
        return self.post("/user/info/batchget", data)

    def user_get(self, next_openid=None):
        """
        获取公众号关注列表
        一次最多返回1000个

        :param next_openid: 第一个拉取的openid,不填默认从头开始
        """
        args = dict()
        if next_openid:
            args.setdefault("next_openid", next_openid)
        return self.get("/user/get", args)

    def menu_create(self, data):
        data = dict(button=data)
        return self.post("/menu/create", data)

    def menu_get(self):
        return self.get("/menu/get")

    def menu_delete(self):
        return self.get("/menu/delete")

    def get_current_selfmenu_info(self):
        return self.get("/get_current_selfmenu_info")

    def shorturl(self, long_url):
        """
        长链接转为短链接

        :param long_url: 长链接
        """
        data = dict(action="long2short", long_url=long_url)
        return self.post("/shorturl", data)

    def qrcode_create(self, scene_id, expires=30):
        """
        创建qrcode
        """
        data = dict(
            action_name="QR_SCENE", expire_seconds=expires,
            action_info=dict(scene=dict(scene_id=scene_id)),
        )
        return self.post("/qrcode/create", data)

    def qrcode_create_limit(self, input):
        """
        创建qrcode限制方式
        """
        data = dict()
        if isinstance(input, int):
            data["action_name"] = "QR_LIMIT_SCENE"
            data["action_info"] = dict(scene=dict(
                scene_id=input,
            ))
        elif isinstance(input, str):
            data["action_name"] = "QR_LIMIT_STR_SCENE"
            data["action_info"] = dict(scene=dict(
                scene_str=input,
            ))
        else:
            raise ValueError("invalid type")
        return self.post("/qrcode/create", data)

    def qrcode_show(self, ticket):
        """
        显示qrcode
        """
        url = "https://mp.weixin.qq.com/cgi-bin/showqrcode"
        return self.add_query(url, dict(ticket=ticket))

    def shop_list(self, pageindex=1, pagesize=10):
        """
        门店列表
        """
        data = dict(pageindex=pageindex, pagesize=pagesize)
        return self.post("/shop/list", data, prefix="/bizwifi")

    def shop_get(self, shop_id):
        """
        查询门店Wi-Fi信息
        """
        return self.post("/shop/get", dict(shop_id=shop_id), prefix="/bizwifi")

    def shop_update(self, shop_id, old_ssid, ssid, password=None):
        """
        修改门店网络信息
        """
        data = dict(shop_id=shop_id, old_ssid=old_ssid, ssid=ssid)
        if password:
            data.update(dict(password=password))
        return self.post("/shop/update", data, prefix="/bizwifi")

    def shop_clean(self, shop_id):
        """
        通过此接口清空门店的网络配置及所有设备，恢复空门店状态
        """
        return self.post("/shop/clean", dict(shop_id=shop_id), prefix="/bizwifi")

    def apportal_register(self, shop_id, ssid, reset):
        """
        添加portal型设备
        """
        data = dict(shop_id=shop_id, ssid=ssid, reset=reset)
        return self.post("/apportal/register", data)

    def device_list(self, shop_id=None, pageindex=1, pagesize=10, prefix="/bizwifi"):
        """
        查询设备
        """
        data = dict(pageindex=pageindex, pagesize=pagesize)
        if shop_id:
            data.update(dict(shop_id=shop_id))
        return self.post("/device/list", data, prefix="/bizwifi")

    def device_delete(self, bssid):
        """
        删除设备
        """
        return self.post("/device/delete", dict(bssid=bssid), prefix="/bizwifi")

    def qrcode_get(self, shop_id, ssid, img_id):
        """
        获取物料二维码
        """
        data = dict(shop_id=shop_id, ssid=ssid, img_id=img_id)
        return self.post("/qrcode/get", data, prefix="/bizwifi")

    def get_all_private_template(self):
        """
        获取所有私有模板列表
        """
        return self.get("/template/get_all_private_template")

    def del_private_template(self, template_id):
        """
        删除私有模板
        """
        return self.post("/template/del_private_template", dict(template_id=template_id))

    def template_send(self, template_id, touser, data, url=None, miniprogram=None, **kwargs):
        """
        发送模板消息

        :paramas template_id: 模板id
        :params touser: openid
        :params data: 模板消息对应的内容跟颜色
        :params url: 跳转地址
        :parms miniprogram: 小程序跳转相关
        """
        kwargs.setdefault("template_id", template_id)
        kwargs.setdefault("touser", touser)
        kwargs.setdefault("data", data)
        url and kwargs.setdefault("url", url)
        miniprogram and kwargs.setdefault("miniprogram", miniprogram)
        # print kwargs
        return self.post("/message/template/send", kwargs)
