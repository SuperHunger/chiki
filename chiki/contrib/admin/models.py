# coding: utf-8
from chiki.base import db
from chiki.utils import sign
from datetime import datetime
from flask import current_app
from werkzeug.utils import cached_property
from chiki.utils import get_ip, get_spm


class AdminUser(db.Document):
    """ 管理员 """

    username = db.StringField(verbose_name='用户')
    password = db.StringField(verbose_name='密码')
    group = db.ReferenceField('Group', verbose_name='组')
    root = db.BooleanField(default=False, verbose_name='超级管理员')
    active = db.BooleanField(default=True, verbose_name='激活')
    freezed = db.DateTimeField(verbose_name='冻结时间')
    logined = db.DateTimeField(default=datetime.now, verbose_name='登录时间')
    modified = db.DateTimeField(default=datetime.now, verbose_name='修改时间')
    created = db.DateTimeField(default=datetime.now, verbose_name='创建时间')

    def __unicode__(self):
        return self.username

    def is_user(self):
        return True

    def is_authenticated(self):
        """ 是否登录 """
        return True

    def is_active(self):
        """ 是否激活 """
        return self.active

    def is_anonymous(self):
        """ 是否游客 """
        return False

    def get_id(self):
        s = sign(current_app.config.get('SECRET_KEY'), password=self.password)
        return '{0}|{1}'.format(self.id, s)


class Group(db.Document):
    """ 管理组 """

    name = db.StringField(verbose_name='组名')
    power = db.ListField(db.ReferenceField('View'), verbose_name='使用权限')
    can_create = db.ListField(db.ReferenceField('View'), verbose_name='创建权限')
    can_edit = db.ListField(db.ReferenceField('View'), verbose_name='编辑权限')
    can_delete = db.ListField(db.ReferenceField('View'), verbose_name='删除权限')
    modified = db.DateTimeField(default=datetime.now, verbose_name='修改时间')
    created = db.DateTimeField(default=datetime.now, verbose_name='创建时间')

    def __unicode__(self):
        return self.name

    @cached_property
    def power_list(self):
        return [x.name for x in self.power]

    @cached_property
    def can_create_list(self):
        return [x.name for x in self.can_create]

    @cached_property
    def can_edit_list(self):
        return [x.name for x in self.can_edit]

    @cached_property
    def can_delete_list(self):
        return [x.name for x in self.can_delete]


class AdminUserLoginLog(db.Document):
    """ 管理登录日志 """

    TYPE = db.choices(login='登录', logout='退出', error='密码错误')

    user = db.ReferenceField('AdminUser', verbose_name='用户')
    type = db.StringField(choices=TYPE.CHOICES, verbose_name='类型')
    spm = db.StringField(max_length=100, verbose_name='SPM')
    ip = db.StringField(max_length=20, verbose_name='IP')
    created = db.DateTimeField(default=datetime.now, verbose_name='创建时间')

    def __unicode__(self):
        return '%s' % self.user.username

    @staticmethod
    def log(user, type, spm=None, ip=None):
        spm = spm if spm else get_spm()
        ip = ip if ip else get_ip()
        AdminUserLoginLog(user=user, type=type, spm=spm, ip=ip).save()

    @staticmethod
    def login(user):
        AdminUserLoginLog.log(user, AdminUserLoginLog.TYPE.LOGIN)

    @staticmethod
    def logout(user):
        AdminUserLoginLog.log(user, AdminUserLoginLog.TYPE.LOGOUT)

    @staticmethod
    def error(user):
        AdminUserLoginLog.log(user, AdminUserLoginLog.TYPE.ERROR)


class AdminChangeLog(db.Document):
    """ 管理员操作日志 """

    TYPE = db.choices(edit='修改', created='创建', delete='删除')

    user = db.ReferenceField('AdminUser', verbose_name='用户')
    model = db.StringField(verbose_name='模块')
    before_data = db.StringField(verbose_name='操作前')
    after_data = db.StringField(verbose_name='操作后')
    type = db.StringField(verbose_name='类型', choices=TYPE.CHOICES)
    created = db.DateTimeField(default=datetime.now, verbose_name='创建时间')
