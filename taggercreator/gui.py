import os
import re
from PyQt6.QtGui import QDoubleValidator, QFont
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from . import core
from . import notificator


def clear_layout(layout):
    if layout:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                clear_layout(item.layout())


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()
        cfg = core.container.cfg

        self.notifier = core.container.notifier()
        self.main_layout = QVBoxLayout(self)

        # scroll_area = QScrollArea(self)
        # scroll_area.setObjectName("ScrollArea")
        # scroll_area.setStyleSheet("#ScrollArea {border: 0px solid black}")
        # scroll_area.setWidgetResizable(True)

        # self.main_layout.addWidget(scroll_area)

        self.creator_widget = CreatorWidget(self)
        self.main_layout.addWidget(self.creator_widget)

        self.setLayout(self.main_layout)
        self.resize(cfg.window.open_width(), cfg.window.open_height())
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        render_cfg = core.container.cfg.render.main_window
        # self.setStyleSheet(f"background-color:{render_cfg.background_color()}")

    def keyPressEvent(self, event):
        modifier = ''
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            modifier += 'Ctrl+'
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            modifier += 'Shift+'
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            modifier += 'Alt+'

        # key = event.text().upper()
        # if not key:
        key = Qt.Key(event.key()).name

        notification = notificator.Notification(notificator.Messages.key_event)
        notification.key = f"{modifier}{key}"
        self.notifier.notify(notification)

        super().keyPressEvent(event)


class CreatorWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        notifier = core.container.notifier()

        self.custom_layout = QVBoxLayout(self)

        cwd = CurrentWorkingDirectoryWidget(self)
        self.custom_layout.addWidget(cwd)

        self.profile_selector = ProfileSelectorWidget(self)
        self.custom_layout.addWidget(self.profile_selector)

        self.path_template = PathTemplateWidget(self)
        self.custom_layout.addWidget(self.path_template)

        self.tags_editor = TagsEditor(self)
        self.custom_layout.addWidget(self.tags_editor)

        self.subdirectories = SubDirectoriesWidget(self)
        self.custom_layout.addWidget(self.subdirectories)

        self.switches = SwitchesWidget(self)
        self.custom_layout.addWidget(self.switches)

        self.control = ControlWidget(self)
        self.custom_layout.addWidget(self.control)

        self.custom_layout.setSpacing(1)
        self.custom_layout.setContentsMargins(1, 1, 1, 1)

        self.setLayout(self.custom_layout)

        self.profile_selector.init_profiles()

        # self.setObjectName("ViewFrame")
        # self.setStyleSheet("#ViewFrame {border: 0px solid black}")

        # self.update_view()


class CurrentWorkingDirectoryWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        notifier = core.container.notifier()

        self.custom_layout = QHBoxLayout(self)

        self.label = QLabel(f"{os.getcwd()}")
        self.button = QPushButton("change")

        self.custom_layout.addWidget(self.label)
        self.custom_layout.addStretch()
        # self.custom_layout.addWidget(self.button)

        self.setLayout(self.custom_layout)

        self.custom_layout.setSpacing(1)
        self.custom_layout.setContentsMargins(1, 1, 1, 1)


class ProfileSelectorWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.notifier = core.container.notifier()

        self.custom_layout = QVBoxLayout(self)

        self.label = QLabel("Profile")
        self.box = QComboBox()
        self.box.currentIndexChanged.connect(self.on_combobox_changed)

        self.custom_layout.addWidget(self.label)
        self.custom_layout.addWidget(self.box)

        self.setLayout(self.custom_layout)

        self.custom_layout.setSpacing(1)
        self.custom_layout.setContentsMargins(1, 1, 1, 1)

    def init_profiles(self):
        self.box.addItems(list(core.container.profiles_cfg()))

    def on_combobox_changed(self, index):
        notification = notificator.Notification(notificator.Messages.profile_change)
        notification.profile = self.box.currentText()
        self.notifier.notify(notification)


class PathTemplateWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.notifier = core.container.notifier()
        self.notifier.subscribe(notificator.Messages.profile_change, self.profile_change)

        self.custom_layout = QVBoxLayout(self)

        self.label = QLabel("Path Template")
        self.edit = QLineEdit()

        self.custom_layout.addWidget(self.label)
        self.custom_layout.addWidget(self.edit)

        self.setLayout(self.custom_layout)

        self.custom_layout.setSpacing(1)
        self.custom_layout.setContentsMargins(1, 1, 1, 1)

    def profile_change(self, notification):
        profile_cfg = core.container.profiles_cfg()[notification.profile]
        self.edit.setText(profile_cfg["path.template"])


class TagsEditor(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_ui()

        # self.tags = []

        self.notifier = core.container.notifier()
        self.notifier.subscribe(notificator.Messages.profile_change, self.profile_change)
        # self.notifier.subscribe(notificator.Messages.new_tags, self.load_new_tags_from_notification)

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.top_layout = QVBoxLayout()
        self.top_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.bottom_layout = QVBoxLayout()

        # Scroll Area Settings
        self.scroll_area = QScrollArea()
        self.scroll_area_widget_contents = QWidget()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area_widget_contents.setLayout(self.top_layout)
        self.scroll_area.setWidget(self.scroll_area_widget_contents)

        # Add Tag Button
        self.add_tag_button = QPushButton("Přidat tag")
        self.add_tag_button.clicked.connect(lambda: self.add_tag_line(""))

        # self.top_layout.addStretch()

        self.bottom_layout.addWidget(self.add_tag_button)
        self.layout.addWidget(self.scroll_area)
        self.layout.addLayout(self.bottom_layout)

        self.top_layout.setSpacing(0)
        self.top_layout.setContentsMargins(0, 0, 0, 0)

        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)

    def profile_change(self, notification):
        self.clear_tags()
        profile_cfg = core.container.profiles_cfg()[notification.profile]
        self.clear_and_load(profile_cfg["tags"])

    def add_tag_line(self, tag):
        # # Line Edit for the tag
        # line_edit = QLineEdit()
        # line_edit.setText(tag)
        #
        # # Remove Button for each tag line
        # remove_button = QPushButton("Odstranit")
        # remove_button.clicked.connect(lambda: self.remove_tag_line(line_edit, remove_button))
        #
        # # Horizontal layout for the tag line
        # h_layout = QHBoxLayout()
        # h_layout.addWidget(line_edit)
        # h_layout.addWidget(remove_button)
        #
        # # Insert the new tag line at the second to last position (above the add button)
        # self.layout.insertLayout(self.layout.count() - 1, h_layout)


        te = TagEditor()
        te.line_edit.setText(tag)
        self.top_layout.addWidget(te, alignment=Qt.AlignmentFlag.AlignTop)
        te.line_edit.setFocus()

        # def remove_tag_line(self, line_edit, remove_button):
    #     # Remove tag line from the layout
    #     for i in reversed(range(self.layout.count())):
    #         widget = self.layout.itemAt(i).widget()
    #         if widget == line_edit or widget == remove_button:
    #             widget.deleteLater()
    #             self.layout.removeItem(self.layout.itemAt(i))

    def remove_tag_line(self, line_edit, remove_button):
        # Find the parent layout of the line_edit and remove_button
        parent_layout = None
        for i in range(self.top_layout.count()):
            layout = self.top_layout.itemAt(i)
            if layout is not None:
                layout_widget = layout.itemAt(0)  # Get the first item in the horizontal layout
                if layout_widget is not None and (
                        layout_widget.widget() == line_edit or layout_widget.widget() == remove_button):
                    parent_layout = layout
                    break

        if parent_layout:
            # Remove all widgets in this horizontal layout
            while parent_layout.count():
                item = parent_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            # Remove the horizontal layout itself from the main layout
            self.top_layout.removeItem(parent_layout)

    def load_new_tags_from_notification(self, notification):
        self.clear_and_load(notification.tags)

    # def save_and_clear(self):
    #     self.tags = self.get_tags()
    #     self.clear_tags()

    def clear_tags(self):
        # Clear existing tags
        while self.top_layout.count() > 0:  # Keep the add tag button
            child = self.top_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def clear_and_load(self, tags):
        self.clear_tags()
        self.load_tags(tags)

    def load_tags(self, tags):
        # Add new tags
        for tag in tags:
            self.add_tag_line(tag)

    def get_tags(self):
        current_tags = []
        for i in range(self.top_layout.count()):  # Exclude the add button
            item_at = self.top_layout.itemAt(i)
            if not isinstance(item_at, QWidgetItem):
                continue
            tag_editor = item_at.widget()
            if isinstance(tag_editor, TagEditor):
                text = tag_editor.line_edit.text().strip()
                if text != "":
                    current_tags.append(text)
        return current_tags


class TagEditor(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_ui()
        self.notifier = core.container.notifier()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.line_edit = QLineEdit()
        self.line_edit.setCompleter(self.completer())
        self.line_edit.setText("")

        # Remove Button for each tag line
        # remove_button = QPushButton("Odstranit")
        remove_button = QPushButton()
        path = os.path.join(core.container.package_paths().image_directory(), 'delete.png')
        remove_button.setIcon(QIcon(path))
        remove_button.clicked.connect(self.remove_itself)

        # Horizontal layout for the tag line
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.line_edit)
        self.layout.addWidget(remove_button)

        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)

    def remove_itself(self):
        self.setParent(None)
        self.deleteLater()

    def completer(self):
        templates = core.container.cfg.templates()
        completer_model = QStringListModel(templates)
        completer = QCompleter()
        completer.setModel(completer_model)
        return completer


class SubDirectoriesWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.notifier = core.container.notifier()
        self.notifier.subscribe(notificator.Messages.profile_change, self.profile_change)

        self.custom_layout = QVBoxLayout(self)

        self.label = QLabel("Subdirectories")
        self.edit = QLineEdit()

        self.custom_layout.addWidget(self.label)
        self.custom_layout.addWidget(self.edit)

        self.setLayout(self.custom_layout)

        self.custom_layout.setSpacing(1)
        self.custom_layout.setContentsMargins(1, 1, 1, 1)

    def profile_change(self, notification):
        profile_cfg = core.container.profiles_cfg()[notification.profile]
        sub_directories = profile_cfg["sub.directories"]
        self.edit.setText(",".join(sub_directories))

    def sub_directories_list(self):
        return re.split(r'[ ,;]+', self.edit.text())


class SwitchesWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.notifier = core.container.notifier()
        self.notifier.subscribe(notificator.Messages.profile_change, self.profile_change)

        self.custom_layout = QVBoxLayout(self)

        self.supress_timestamp_auto_tagging = QCheckBox("Supress timestamp auto tagging")
        self.supress_machine_auto_tagging = QCheckBox("Supress machine auto tagging")
        self.supress_mac_address_auto_tagging = QCheckBox("Supress mac address auto tagging")

        self.custom_layout.addWidget(self.supress_timestamp_auto_tagging)
        self.custom_layout.addWidget(self.supress_machine_auto_tagging)
        self.custom_layout.addWidget(self.supress_mac_address_auto_tagging)

        self.setLayout(self.custom_layout)

        self.custom_layout.setSpacing(1)
        self.custom_layout.setContentsMargins(1, 1, 1, 1)

    def profile_change(self, notification):
        profile_cfg = core.container.profiles_cfg()[notification.profile]
        # "timestamp.auto.tagging": "True",
        # "machine.auto.tagging": "True",
        # "mac.address.auto.tagging": "True"
        self.supress_timestamp_auto_tagging.setChecked(not self.to_boolean(profile_cfg["timestamp.auto.tagging"]))
        self.supress_machine_auto_tagging.setChecked(not self.to_boolean(profile_cfg["machine.auto.tagging"]))
        self.supress_mac_address_auto_tagging.setChecked(not self.to_boolean(profile_cfg["mac.address.auto.tagging"]))

    def to_boolean(self, text):
        return True if text.strip().lower() == "true" else False


class ControlWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.notifier = core.container.notifier()

        self.custom_layout = QVBoxLayout(self)

        self.button = QPushButton("Create")
        self.button.clicked.connect(self.create)
        self.custom_layout.addWidget(self.button)

        self.setLayout(self.custom_layout)

        self.custom_layout.setSpacing(1)
        self.custom_layout.setContentsMargins(1, 1, 1, 1)

    def create(self):
        notification = notificator.Notification(notificator.Messages.create)
        self.notifier.notify(notification)
