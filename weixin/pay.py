# -*- coding: utf-8 -*-


from __future__ import unicode_literals

import time
import string
import random
import hashlib
import requests

from .base import Map, WeixinError

try:
    from flask import request
except Exception:
    request = None

from lxml import etree


__all__ = ("WeixinPayError", "WeixinPay")


FAIL = "FAIL"
SUCCESS = "SUCCESS"


class WeixinPayError(WeixinError):

    def __init__(self, msg):
        super(WeixinPayError, self).__init__(msg)


class WeixinPay(object):
    PAY_HOST = "https://api.mch.weixin.qq.com"

    def __init__(self, app_id, mch_id, mch_key, notify_url, key=None, cert=None):
        self.app_id = app_id
        self.mch_id = mch_id
        self.mch_key = mch_key
        self.notify_url = notify_url
        self.key = key
        self.cert = cert
        self.sess = requests.Session()

    @property
    def remote_addr(self):
        if request is not None:
            return request.remote_addr
        return ""

    @property
    def nonce_str(self):
        char = string.ascii_letters + string.digits
        return "".join(random.choice(char) for _ in range(32))

    def sign(self, raw):
        raw = [(k, str(raw[k]) if isinstance(raw[k], int) else raw[k])
               for k in sorted(raw.keys())]
        s = "&".join("=".join(kv) for kv in raw if kv[1])
        s += "&key={0}".format(self.mch_key)
        return hashlib.md5(s.encode("utf-8")).hexdigest().upper()

    def check(self, data):
        sign = data.pop("sign")
        return sign == self.sign(data)

    def to_xml(self, raw):
        s = ""
        for k, v in raw.items():
            s += "<{0}>{1}</{0}>".format(k, v)
        s = "<xml>{0}</xml>".format(s)
        return s.encode("utf-8")

    def to_dict(self, content):
        raw = {}
        root = etree.fromstring(content.encode("utf-8"),
                                parser=etree.XMLParser(resolve_entities=False))
        for child in root:
            raw[child.tag] = child.text
        return raw

    def _fetch(self, url, data, use_cert=False):
        data.setdefault("appid", self.app_id)
        data.setdefault("mch_id", self.mch_id)
        data.setdefault("nonce_str", self.nonce_str)
        data.setdefault("sign", self.sign(data))

        if use_cert:
            resp = self.sess.post(url, data=self.to_xml(data), cert=(self.cert, self.key))
        else:
            resp = self.sess.post(url, data=self.to_xml(data))
        content = resp.content.decode("utf-8")
        if "return_code" in content:
            data = Map(self.to_dict(content))
            if data.return_code == FAIL:
                raise WeixinPayError(data.return_msg)
            if "result_code" in content and data.result_code == FAIL:
                raise WeixinPayError(data.err_code_des)
            return data
        return content

    def reply(self, msg, ok=True):
        code = SUCCESS if ok else FAIL
        return self.to_xml(dict(return_code=code, return_msg=msg))

    def unified_order(self, **data):
        """
        统一下单
        out_trade_no、body、total_fee、trade_type必填
        app_id, mchid, nonce_str自动填写
        spbill_create_ip 在flask框架下可以自动填写, 非flask框架需要主动传入此参数
        """
        url = self.PAY_HOST + "/pay/unifiedorder"

        # 必填参数
        if "out_trade_no" not in data:
            raise WeixinPayError("缺少统一支付接口必填参数out_trade_no")
        if "body" not in data:
            raise WeixinPayError("缺少统一支付接口必填参数body")
        if "total_fee" not in data:
            raise WeixinPayError("缺少统一支付接口必填参数total_fee")
        if "trade_type" not in data:
            raise WeixinPayError("缺少统一支付接口必填参数trade_type")

        # 关联参数
        if data["trade_type"] == "JSAPI" and "openid" not in data:
            raise WeixinPayError("trade_type为JSAPI时，openid为必填参数")
        if data["trade_type"] == "NATIVE" and "product_id" not in data:
            raise WeixinPayError("trade_type为NATIVE时，product_id为必填参数")
        data.setdefault("notify_url", self.notify_url)
        if "spbill_create_ip" not in data:
            data.setdefault("spbill_create_ip", self.remote_addr)

        raw = self._fetch(url, data)
        return raw

    def jsapi(self, **kwargs):
        """
        生成给JavaScript调用的数据
        详细规则参考 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=7_7&index=6
        """
        kwargs.setdefault("trade_type", "JSAPI")
        raw = self.unified_order(**kwargs)
        package = "prepay_id={0}".format(raw["prepay_id"])
        timestamp = str(int(time.time()))
        nonce_str = self.nonce_str
        raw = dict(appId=self.app_id, timeStamp=timestamp,
                   nonceStr=nonce_str, package=package, signType="MD5")
        sign = self.sign(raw)
        return dict(package=package, appId=self.app_id, signType="MD5",
                    timeStamp=timestamp, nonceStr=nonce_str, sign=sign)

    def order_query(self, **data):
        """
        订单查询
        out_trade_no, transaction_id至少填一个
        appid, mchid, nonce_str不需要填入
        """
        url = self.PAY_HOST + "/pay/orderquery"

        if "out_trade_no" not in data and "transaction_id" not in data:
            raise WeixinPayError("订单查询接口中，out_trade_no、transaction_id至少填一个")

        return self._fetch(url, data)

    def close_order(self, out_trade_no, **data):
        """
        关闭订单
        out_trade_no必填
        appid, mchid, nonce_str不需要填入
        """
        url = self.PAY_HOST + "/pay/closeorder"

        data.setdefault("out_trade_no", out_trade_no)

        return self._fetch(url, data)

    def refund(self, **data):
        """
        申请退款
        out_trade_no、transaction_id至少填一个且
        out_refund_no、total_fee、refund_fee、op_user_id为必填参数
        appid、mchid、nonce_str不需要填入
        """
        url = self.PAY_HOST + "/secapi/pay/refund"
        if not self.key or not self.cert:
            raise WeixinError("退款申请接口需要双向证书")
        if "out_trade_no" not in data and "transaction_id" not in data:
            raise WeixinPayError("退款申请接口中，out_trade_no、transaction_id至少填一个")
        if "out_refund_no" not in data:
            raise WeixinPayError("退款申请接口中，缺少必填参数out_refund_no");
        if "total_fee" not in data:
            raise WeixinPayError("退款申请接口中，缺少必填参数total_fee");
        if "refund_fee" not in data:
            raise WeixinPayError("退款申请接口中，缺少必填参数refund_fee");

        return self._fetch(url, data, True)

    def refund_query(self, **data):
        """
        查询退款
        提交退款申请后，通过调用该接口查询退款状态。退款有一定延时，
        用零钱支付的退款20分钟内到账，银行卡支付的退款3个工作日后重新查询退款状态。

        out_refund_no、out_trade_no、transaction_id、refund_id四个参数必填一个
        appid、mchid、nonce_str不需要填入
        """
        url = self.PAY_HOST + "/pay/refundquery"
        if "out_refund_no" not in data and "out_trade_no" not in data \
                and "transaction_id" not in data and "refund_id" not in data:
            raise WeixinPayError("退款查询接口中，out_refund_no、out_trade_no、transaction_id、refund_id四个参数必填一个")

        return self._fetch(url, data)

    def download_bill(self, bill_date, bill_type="ALL", **data):
        """
        下载对账单
        bill_date、bill_type为必填参数
        appid、mchid、nonce_str不需要填入
        """
        url = self.PAY_HOST + "/pay/downloadbill"
        data.setdefault("bill_date", bill_date)
        data.setdefault("bill_type", bill_type)

        if "bill_date" not in data:
            raise WeixinPayError("对账单接口中，缺少必填参数bill_date")

        return self._fetch(url, data)

    def pay_individual(self, **data):
        """
        企业付款到零钱
        """
        url = "https://api.mch.weixin.qq.com/mmpaymkttransfers/promotion/transfers"
        if not self.key or not self.cert:
            raise WeixinPayError("企业接口需要双向证书")
        if "partner_trade_no" not in data:
            raise WeixinPayError("企业付款接口中, 缺少必要的参数partner_trade_no")
        if "openid" not in data:
            raise WeixinPayError("企业付款接口中，缺少必填参数openid")
        if "amount" not in data:
            raise WeixinPayError("企业付款接口中，缺少必填参数amount")
        if "desc" not in data:
            raise WeixinPayError("企业付款接口中，缺少必填参数desc")
        data.setdefault('check_name', 'NO_CHECK')
        return self._fetch_pay(url, data, True)

    def pay_individual_to_card(self, **data):
        """企业付款到银行卡"""
        url = 'https://api.mch.weixin.qq.com/mmpaysptrans/pay_bank'
        if not self.key or not self.cert:
            raise WeixinPayError("企业接口需要双向证书")
        if "partner_trade_no" not in data:
            raise WeixinPayError("企业付款接口中, 缺少必要的参数partner_trade_no")
        if "enc_bank_no" not in data:
            raise WeixinPayError("企业付款接口中，缺少必填参数enc_bank_no")
        if "enc_true_name" not in data:
            raise WeixinPayError("企业付款接口中，缺少必填参数enc_true_name")
        if "bank_code" not in data:
            raise WeixinPayError("企业付款接口中，缺少必填参数bank_code")
        if "amount" not in data:
            raise WeixinPayError("企业付款接口中，缺少必填参数amount")
        return self._fetch(url, data, True)

    def pay_individual_bank_query(self, **data):
        """企业付款到银行卡查询"""
        url = "https://api.mch.weixin.qq.com/mmpaysptrans/query_bank"
        if not self.key or not self.cert:
            raise WeixinPayError("企业接口需要双向证书'")
        if "partner_trade_no" not in data:
            raise WeixinPayError("企业付款接口中, 缺少必要的参数partner_trade_no")
        return self._fetch(url, data, True)

    def pay_individual_query(self, **data):
        """企业付款到零钱查询"""
        url = "https://api.mch.weixin.qq.com/mmpaymkttransfers/gettransferinfo"
        if not self.key or not self.cert:
            raise WeixinPayError("企业接口需要双向证书'")
        if "partner_trade_no" not in data:
            raise WeixinPayError("企业付款接口中, 缺少必要的参数partner_trade_no")
        return self._fetch(url, data, True)

    def _fetch_pay(self, url, data, use_cert=False):
        data.setdefault("mch_appid", self.app_id)
        data.setdefault("mchid", self.mch_id)
        data.setdefault("nonce_str", self.nonce_str)
        data.setdefault("sign", self.sign(data))
        if use_cert:
            resp = self.sess.post(url, data=self.to_xml(data), cert=(self.cert, self.key))
        else:
            resp = self.sess.post(url, data=self.to_xml(data))
        content = resp.content.decode("utf-8")
        if "return_code" in content:
            data = Map(self.to_dict(content))
            if data.return_code == FAIL:
                raise WeixinPayError(data.return_msg)
            if "result_code" in content and data.result_code == FAIL:
                raise WeixinPayError(data.err_code_des)
            return data
        return content
