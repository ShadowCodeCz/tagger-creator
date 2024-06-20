import json
import os
import ctypes
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import *

# import app_core
import qdarktheme
import datetime
import subprocess

from . import core
from . import gui
from . import notificator


class ApplicationCLI:
    @staticmethod
    def run(arguments):
        cfg = core.container.cfg
        cfg.from_json(arguments.configuration)
        app = Application()
        app.run()


class Controller:
    def __init__(self):
        self.notifier = core.container.notifier()
        self.load_profiles()
        # self.load_tags()

    def load_profiles(self):
        profiles_config = self.read_json(core.container.cfg.profiles_config())
        core.container.profiles_cfg.override(profiles_config["auto.profiles"])

    def read_json(self, path):
        with open(path) as f:
            return json.load(f)

    # def load_tags(self):
    #     notification = notificator.Notification(notificator.Messages.new_tags)
    #     notification.tags = self.read_tags()
    #     self.notifier.notify(notification)

    # def read_tags(self):
    #     if os.path.exists(self.tagger_file_path):
    #         try:
    #             with open(self.tagger_file_path) as file:
    #                 return json.load(file)
    #         except Exception as e:
    #             return []
    #     else:
    #         return []


class Application:
    def __init__(self, logger=core.container.logger()):
        self.app = None
        self.logger = logger
        self.window = None
        self.arguments = None
        self.controller = Controller()
        self.notifier = core.container.notifier()
        self.notifier.subscribe(notificator.Messages.create, self.create)

    def run(self):
        self.app = QApplication([])
        qdarktheme.setup_theme(corner_shape="sharp")
        self.window = gui.MainWindow()
        self.window.setWindowTitle(f"Template Gui App")
        self.set_logo()

        self.window.show()
        self.app.exec()

    def set_logo(self):
        my_app_id = f'shadowcode.{core.container.app_description().name}.0.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
        path = os.path.join(core.container.package_paths().image_directory(), 'logo.png')
        self.window.setWindowIcon(QIcon(path))
        self.app.setWindowIcon(QIcon(path))

    def create(self, notificator):
        path_template = self.window.creator_widget.path_template.edit.text()
        tags = self.window.creator_widget.tags_editor.get_tags()
        subdirectories = self.window.creator_widget.subdirectories.sub_directories_list()
        supress_timestamp_auto_tagging = self.window.creator_widget.switches.supress_timestamp_auto_tagging.isChecked()
        supress_machine_auto_tagging = self.window.creator_widget.switches.supress_machine_auto_tagging.isChecked()
        supress_mac_address_auto_tagging = self.window.creator_widget.switches.supress_mac_address_auto_tagging.isChecked()

        str_tags = " ".join(tags)
        cmd_tags = f"-t {str_tags}" if len(str_tags) > 0 else ""

        str_sub_dirs = " ".join(subdirectories)
        cmd_sub_dirs = f"-s {str_sub_dirs}" if len(str_sub_dirs) > 0 else ""

        cmd_supress_timestamp_auto_tagging = f"--supress-timestamp-auto-tagging" if supress_timestamp_auto_tagging else ""
        cmd_supress_machine_auto_tagging = f"--supress-machine-auto-tagging" if supress_machine_auto_tagging else ""
        cmd_supress_mac_address_auto_tagging = f"--supress-mac-address-auto-tagging" if supress_mac_address_auto_tagging else ""

        cmd = f'tagger-core mkdir -p "{path_template}" {cmd_tags} {cmd_sub_dirs} {cmd_supress_timestamp_auto_tagging} {cmd_supress_machine_auto_tagging} {cmd_supress_mac_address_auto_tagging}'
        print(cmd)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        p.wait()



