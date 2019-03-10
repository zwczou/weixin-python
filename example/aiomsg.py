import asyncio

from aiohttp import web
from weixin.msg import WeixinMsg

app = web.Application(loop=asyncio.get_event_loop())
msg = WeixinMsg("qwertyuiop", None, 0)

async def res_msg(request):
    print('text: ', await request.text())
    return await msg.aio_view_func(request)

app.add_routes([web.get('/api/wx_msg', res_msg),
                web.post('/api/wx_msg', res_msg)])

@msg.text()
def msg_text(**kwargs):
    print('text: ', kwargs)
    return 'succ'


@msg.text("help")
def msg_help(**kwargs):
    print('text help: ', kwargs)
    return 'help'


@msg.click
def msg_click(**kwargs):
    print('click: ', kwargs)
    return dict(content="Welcome", type="text")


@msg.image
def msg_image(**kwargs):
    print('image: ', kwargs)
    return dict(content="image")


if __name__ == "__main__":
    web.run_app(app, port=80)
