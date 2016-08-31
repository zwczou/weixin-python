# -*- coding: utf-8 -*-


import time
import json
import requests

from map import Map
from urllib import urlencode


__all__ = ("WeixinError", "Weixin")

class WeixinError(Exception):

    def __init__(self, msg):
        super(WeixinError, self).__init__(msg)


class Weixin(object):
    api_uri = "https://api.weixin.qq.com/cgi-bin"

    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.session = requests.Session()
        self._cached = Map()

    def add_query(self, url, args):
        if not args:
            return url
        return url + ('?' in url and '&' or '?') + urlencode(args)

    def fetch(self, method, url, params=None, data=None, headers=None):
        req = requests.Request(method, url, params=params,
                               data=data, headers=headers)
        prepped = req.prepare()
        resp = self.session.send(prepped, timeout=20)
        data = Map(resp.json())
        if data.errcode:
            msg = "%(errcode)d %(errmsg)s" % data
            raise WeixinError(msg)
        return data

    def get(self, path, params=None, token=True):
        url = "{0}{1}".format(self.api_uri, path)
        params = {} if not params else params
        token and params.setdefault("access_token", self.access_token)
        return self.fetch("GET", url, params)

    def post(self, path, data, json_encode=True, token=True):
        url = "{0}{1}".format(self.api_uri, path)
        if token:
            url = self.add_query(url, dict(access_token=self.access_token))
        headers = {}
        if json_encode:
            data = json.dumps(data)
            headers["Content-Type"] = "application/json"
        return self.fetch("POST", url, data=data, headers=headers)

    @property
    def access_token(self):
        """
        获取服务端凭证
        """
        token = self._cached.token
        expires = self._cached.expires
        if not token or expires < time.time():
            params = dict()
            params.setdefault("grant_type", "client_credential")
            params.setdefault("appid", self.app_id)
            params.setdefault("secret", self.app_secret)
            data = self.get("/token", params, False)
            self._cached.token = data.access_token
            self._cached.expires = data.expires_in + time.time() - 1000
        return self._cached.token

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
        data = dict(
            action_name="QR_SCENE", expire_seconds=expires,
            action_info=dict(scene=dict(scene_id=scene_id)),
        )
        return self.post("/qrcode/create", data)

    def qrcode_create_limit(self, input):
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
        url = "https://mp.weixin.qq.com/cgi-bin/showqrcode"
        return self.add_query(url, dict(ticket=ticket))


if __name__ == '__main__':
    app_id, app_secret = "wxa686369357769bb1", "2619b8c64487d0bfe125839ed62d6a98"
    wx = Weixin(app_id, app_secret)
    print wx.access_token
    print wx.access_token
    print wx.get_current_selfmenu_info()
    data = wx.qrcode_create(123)
    print wx.qrcode_show(data.ticket)
