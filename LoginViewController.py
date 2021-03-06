# -*- coding: utf-8 -*

from Database import IDATDBdatabase
from LoginView import LoginFrame
from AppData.AppConfig import AppConfig
from Database import IDATDBdatabase
import Database
import wx
from wx.lib.pubsub import pub
from Radio.MessageType import FrameMessage
from Radio.Radio import Channel
import thread


class LoginFrameController(object):
    def __init__(self, frame=None):
        # type: (LoginFrame) -> None
        self.config = AppConfig()
        self.database = IDATDBdatabase()
        self.is_locked = False

        if frame is None:
            frame = LoginFrame(None, u'登录')
        self.frame = frame
        self.panel = frame.panel
        self.login_button = frame.login_button
        self.remember = frame.remember
        self.login_state = frame.login_state

        self.ip_text_field = frame.ip_text_field
        self.uid_text_field = frame.uid_text_field
        self.pwd_text_field = frame.pwd_text_field

        self.view_loaded()
        self.action_bind()

    def action_bind(self):
        self.login_button.Bind(wx.EVT_BUTTON, self.login)
        self.remember.Bind(wx.EVT_CHECKBOX, self.remember_changed)

    def view_loaded(self):
        if self.config.remember:
            self.remember.Value = True
            self.ip_text_field.Value = self.config.ip
            self.uid_text_field.Value = self.config.uid
            self.pwd_text_field.Value = self.config.password

    def login(self, event):
        if not self.is_locked:
            self.is_locked = True
            uid = self.uid_text_field.Value
            pwd = self.pwd_text_field.Value
            server = self.ip_text_field.Value
            if self.config.remember:
                self.config.uid = uid
                self.config.password = pwd
                self.config.ip = server
            thread.start_new_thread(self.database_connect, (uid, pwd, server))

    def database_connect(self, uid, pwd, server):
        try:
            self.database.connect(uid, pwd, server)
        except Database.ConnectionError:
            wx.CallAfter(lambda: wx.MessageBox(u'请检查登录信息', u'登录失败', wx.OK | wx.ICON_ERROR))
        else:
            wx.CallAfter(lambda: pub.sendMessage(Channel.fmFrame, sender=self.frame, msg=FrameMessage.logged_in))
        finally:
            self.is_locked = False


    def remember_changed(self, event):
        self.config.remember = event.Checked()


if __name__ == '__main__':
    app = wx.App(False)
    controller = LoginFrameController()
    app.MainLoop()