# coding: utf-8
from chiki.contrib.users import um
from flask import current_app
from werobot.reply import TransferCustomerServiceReply
from .robot import WeRoBot
from .admin import *
from .models import *

__all__ = [
    'WXMsg', 'init_wxmsg',
]

robot = WeRoBot()


class WXMsg(object):

    def __init__(self, app=None):
        self.subscribe_callback = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.init_robot(robot)
        robot.init_app(app)
        robot.logger = app.logger

    def init_robot(self, robot):
        @robot.text
        def on_text(message):
            msg = Message.objects(keyword=message.content).first()
            if msg:
                reply = msg.reply(message)
                if reply:
                    return reply

            default_msg = Message.objects(default=True).first()
            if default_msg:
                reply = default_msg.reply(message)
                if reply:
                    return reply
            return TransferCustomerServiceReply(message=message)

        @robot.subscribe
        @robot.scan
        def on_subscribe(message):
            user = um.models.User.get_wechat(mp_openid=message.source)
            if not user:
                user = um.models.User.from_wechat_mp(message.source)

            current_user.logger.error('test1')

            um.models.on_invite(user, int(message.key or 0))

            if self.subscribe_callback:
                res = self.subscribe_callback(user, message)
                if res:
                    return res

            current_user.logger.error('test2')

            if current_app.config.get('NEED_QRCODE') and not user.inviter:
                return '%s，欢迎关注！请取消关注，再通过扫描海报二维码进行关注！' % user.nickname

            if not user.wechat_user.subscribe:
                user.wechat_user.dosubscribe()

            current_user.logger.error('test3')

            follow_msg = Message.objects(follow=True).first()
            if follow_msg:
                reply = follow_msg.reply(message)
                if reply:
                    return reply
            default_msg = Message.objects(default=True).first()
            if default_msg:
                reply = default_msg.reply(message)
                if reply:
                    return reply

            current_user.logger.error('test4')
            return TransferCustomerServiceReply(message=message)

        @robot.unsubscribe
        def on_unsubscribe(message):
            user = um.models.User.get_wechat(mp_openid=message.source)
            if user:
                user.wechat_user.unsubscribe()

    def subscribe_handler(self, callback):
        self.subscribe_callback = callback
        return callback


def init_wxmsg(app):
    if app.config.get('WEROBOT_TOKEN') and app.config.get('WXMSG', True):
        return WXMsg(app)
