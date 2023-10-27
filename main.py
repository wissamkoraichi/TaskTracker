from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, NoTransition, CardTransition
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from schedulebanner import ScheduleBanner
from kivy.uix.label import Label
from functools import partial
from os import walk
from myfirebase import MyFirebase
import requests
import json


class HomeScreen(Screen):
    pass

class AddFriendScreen(Screen):
    pass

class LabelButton(ButtonBehavior, Label):
    pass

class ImageButton(ButtonBehavior, Image):
    pass

class LoginScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class ChangeAvatarScreen(Screen):
    pass



GUI = Builder.load_file("main.kv")
class MainApp(App):
    my_friend_id = 1

    def build(self):
        self.my_firebase = MyFirebase()
        return GUI

    def on_start(self):
        # populate avatar grid
        avatar_grid = self.root.ids['change_avatar_screen'].ids['avatar_grid']
        for root_dir, folders, files in walk("icons/avatars/"):
            for f in files:
                img = ImageButton(source="icons/avatars/" + f, on_release=partial(self.change_avatar, f))
                avatar_grid.add_widget(img)
        try:
            with open("refresh_token.txt", 'r') as f:
                refresh_token = f.read()
            id_token, local_id = self.my_firebase.exchange_refresh_token(refresh_token)
            #get database
            result = requests.get("https://task-track-298b9-default-rtdb.firebaseio.com/" + local_id + ".json?auth=" + id_token)
            print("res ok?", result.ok)
            print(result.json())
            data = json.loads(result.content.decode())

            #get avatar image
            avatar_image = self.root.ids['avatar_image']
            avatar_image.source = "icons/avatars/" + data['avatar']



            task_label = self.root.ids['home_screen'].ids['task_label']
            task_label.text = "number of tasks left" + str(data['tasksleft'])

            # Get and update friend id label
            friend_id_label = self.root.ids['settings_screen'].ids['friend_id_label']
            friend_id_label.text = "Friend ID:" + str(self.my_friend_id)

            banner_grid = self.root.ids['home_screen'].ids['banner_grid']
            schedules = data['schedules'][1:]
            for schedule in schedules:
                for i in range(5):

                    s = ScheduleBanner(schedule_image=schedule['schedule_image'], description=schedule['description'],
                                       type_image=schedule['type_image'], number=str(schedule['number']),
                                       units=schedule['units'], assignments=str(schedule['assignments']))
                    banner_grid.add_widget(s)
            self.root.ids['screen_manager'].transition = NoTransition()
            self.change_screen("home_screen")
            self.root.ids['screen_manager'].transition = CardTransition()
        except Exception as e:
            print(e)
            pass

    def change_avatar(self, image, widget_id):
        #change avatar in app
        avatar_image = self.root.ids['avatar_image']
        avatar_image.source = "icons/avatars/" + image

        #switch avatar in firebase
        my_data = '{"avatar": %s}' % image
        requests.patch("https://task-track-298b9-default-rtdb.firebaseio.com/" + str(self.my_friend_id) + ".json",
                       data=my_data)
        self.change_screen("settings_screen")

    def change_screen(self, screen_name):
        screen_manager = self.root.ids['screen_manager']
        screen_manager.current = screen_name


MainApp().run()
