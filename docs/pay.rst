微信支付
========


文档
----

微信详细文档\ `请点击`_

初始化
~~~~~~

::

    from weixin.pay import WeixinPay, WeixinPayError
    # 或者
    # from weixin import WeixinPay, WeixinError

    pay = WeixinPay('app_id', 'mch_id', 'mch_key', 'notify_url', '/path/to/key.pem', '/path/to/cert.pem') # 后两个参数可选

统一下单
~~~~~~~~

**注意**:
默认\ ``spbill_create_ip``\ 的值为\ ``request.remote_addr``\ ，如果没有安装flask，请在参数后面带上\ ``spbill_create_ip``

必填参数

-  out_trade_no 商户订单号
-  body 商品描述
-  total_fee 商品费用（分）
-  trade_type 交易类型

条件参数

-  openid 如果\ ``trade_type``\ 为\ ``JSAPI``\ 时必须
-  product_id 如果\ ``trade_type``\ 为\ ``NATIVE``\ 时必须

举例

::

    try:
        out_trade_no = wx_pay.nonce_str
        raw = pay.unified_order(trade_type="JSAPI", openid="openid", body=u"测试", out_trade_no=out_trade_no, total_fee=1, attach="other info")
        print raw
    except WeixinError, e:
        print e.message

网页端调起支付API
~~~~~~~~~~~~~~~~~

必填参数

-  out_trade_no 商户订单号
-  body 商品描述
-  total_fee 商品费用（分）
-  openid 用户标识

返回参数

-  package 订单详情扩展字符串
-  timeStamp 时间戳
-  appId 公众号id
-  nonceStr 随机字符串
-  signType 清明方式
-  sign 签名

::

    try:
        out_trade_no = wx_pay.nonce_str
        raw = pay.jsapi(openid="openid", body=u"测试", out_trade_no=out_trade_no, total_fee=1, attach="other info")
        print raw
    except WeixinError, e:
        print e

查询订单
~~~~~~~~

参数，二选其一

-  out_trade_no 商户订单号
-  transaction_id 微信订单号

使用 ``out_trade_no`` 查询订单

::

    print pay.order_query(out_trade_no=out_trade_no)

或者使用 ``transaction_id`` 查询

::

    print pay.order_query(transaction_id='transaction_id')

关闭订单
~~~~~~~~

必填参数

-  out_trade_no 商户订单号

举例

::

    print pay.order_close(out_trade_no=out_trade_no)

申请退款
~~~~~~~~

参数，二选其一，必选填写key,cert文件地址

-  out_trade_no 商户订单号
-  transaction_id 微信订单号

使用 ``out_trade_out`` 退款

::

    print pay.refund(out_trade_no=out_trade_no)

或者使用 ``transaction_id`` 退款

::

    print pay.refund(transaction_id='transaction_id')

退款查询
~~~~~~~~

参数，4选一 \* out_trade_no 商户订单号 \* transaction_id 微信订单号 \*
out_refund_no 商户退款单号 \* refund_id 微信退款单号

使用 ``out_trade_no`` 退款

::

    print pay.refund_query(out_trade_no=out_trade_no)

工具函数
~~~~~~~~

签名
^^^^

::

    sign = pay.sign(dict(a='b', b=2, c=3))

验证签名
^^^^^^^^

::

    pay.check(data(a='b', b=2, c=3, sign=sign))

回复消息
^^^^^^^^

::

    pay.reply("OK", True)

    pay.reply("签名验证失败", False)

下载账单
~~~~~~~~

必填参数

-  bill_date 账单日期

举例

::

    print pay.download_bill('20140603')


企业付款
~~~~~~~~

必填参数

-  openid 用户身份, amount 金额(分), partner_trade_no 商户订单号  desc企业付款备注

举例

::

    raw = self.pay.pay_individual(openid=openid, amount=amount, partner_trade_no=partner_trade_no, desc=desc)
    print raw


查询企业付款
~~~~~~~~

必填参数

-  partner_trade_no 商户订单号

举例

::

    raw = self.pay.pay_individual_query(partner_trade_no=partner_trade_no)
    print raw

用法
----

::

    # -*- coding: utf-8 -*-

    # from weixin import WeixinPay, WeixinError
    from weixin.pay import WeixinPay, WeixinPayError


    wx_pay = WeixinPay(app_id, mch_id, mch_key, notify_url)


    @app.route("/pay/create")
    def pay_create():
        """
        微信JSAPI创建统一订单，并且生成参数给JS调用
        """
        try:
            out_trade_no = wx_pay.nonce_str
            raw = wx_pay.jsapi(openid="openid", body=u"测试", out_trade_no=out_trade_no, total_fee=1)
            return jsonify(raw)
        except WeixinPayError, e:
        # except WeixinError, e
            print e.message
            return e.message, 400


    @app.route("/pay/notify")
    def pay_notify():
        """
        微信异步通知
        """
        data = wx_pay.to_dict(request.data)
        if not wx_pay.check(data):
            return wx_pay.reply("签名验证失败", False)
        # 处理业务逻辑
        return wx_pay.reply("OK", True)


    if __name__ == '__main__':
        app.run()


.. _请点击: https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_1
