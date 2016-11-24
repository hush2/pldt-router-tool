import os

from kivy.uix.label import Label

os.environ['KIVY_NO_FILELOG'] = '1'

import kivy

kivy.require('1.9.1')

from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemLabel
from kivy.app import App
import router


class MyListItemLabel(ListItemLabel):
    def __init__(self, **kwargs):
        super().__init__(markup=True, **kwargs)


class RootLayout(BoxLayout):
    list_view = ObjectProperty()
    list_view_container = ObjectProperty()

    def reset_adsl(self):
        lvc = self.list_view_container
        lvc.clear_widgets()
        lvc.add_widget(Label(text='Resetting ADSL connection...'))

    def reboot_router(self):
        lvc = self.list_view_container
        lvc.clear_widgets()
        lvc.add_widget(Label(text='Rebooting router...'))


class MainApp(App):
    def build_config(self, config):
        config.setdefaults('settings', {
            'ip': '192.168.1.1',
            'username': 'admin',
            'password': '1234'})

    def refresh(self, root):
        lvc = root.list_view_container
        lvc.clear_widgets()
        lvc.add_widget(root.list_view)

        try:
            data = router.fetch_data()
            fdata = []
            for (k, v) in data.items():
                fdata.append("{}: [color=#FF0]{}[/color]".format(k, v))
            lv = root.list_view
            lv.adapter.data = fdata
            lv.populate()

        except router.RouterException as e:
            lvc = root.list_view_container
            lvc.clear_widgets()
            lvc.add_widget(Label(text=str(e)))

    def build(self):
        self.title = 'PLDT Router Tool'

        root = RootLayout()

        router.ip = app.config.get('settings', 'ip')
        router.username = app.config.get('settings', 'username')
        router.password = app.config.get('settings', 'password')

        self.refresh(root)

        return root

    def build_settings(self, settings):
        jsondata = '''[
       { "type": "title",
         "title": "Router Settings" },

       { "type": "string",
         "title": "IP Address",
         "desc": "Router IP, if you don't know use default of [b]192.168.1.1[/b].",
         "section": "settings",
         "key": "ip"}      ,

       { "type": "string",
         "title": "Username",
         "desc": "If you did not change username, default is usually [b]admin[/b].",
         "section": "settings",
         "key": "username"},

       { "type": "string",
         "title": "Password",
         "desc": "If you did not change the password, default is usually [b]1234[/b] or [b]1234567890[/b].",
         "section": "settings",
         "key": "password" }]'''

        settings.add_json_panel(self.title, self.config, data=jsondata)


if __name__ == '__main__':
    app = MainApp()
    app.run()
