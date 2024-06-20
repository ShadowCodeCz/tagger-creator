import re


class Messages:
    key_event = "key_event"
    profile_change = "profile.change"
    create = "create"
    # new_tags = "new_tags"


class Notification(object):
    def __init__(self, message, publisher=None):
        self.message = message
        self.publisher = publisher
        self.obj = None


class SingletonNotificationProvider:
    subscription = {}

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonNotificationProvider, cls).__new__(cls)
        return cls.instance

    def subscribe(self, message, subscriber):
        self.subscription.setdefault(message, []).append(subscriber)

    def unsubscribe(self, message, subscriber):
        self.subscription[message].remove(subscriber)

    def notify(self, notification):
        for subscriber in self.subscription.setdefault(notification.message, []):
            subscriber(notification)