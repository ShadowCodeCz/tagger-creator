import hashlib
import re
import json
import logging.config
import os
import glob
import apphelpers as app_helpers
import collections

from dependency_injector import containers, providers
from . import notificator


class Container(containers.DeclarativeContainer):
    app_description = providers.Singleton(app_helpers.AppDescription, "tagger.creator")
    locale_paths = providers.Singleton(app_helpers.LocalePaths, app_description)
    package_paths = providers.Singleton(app_helpers.PackagePaths, app_description(), os.path.dirname(__file__))
    logger_helper = providers.Singleton(app_helpers.LoggerHelper, app_description, locale_paths)
    logger = providers.Factory(logging.getLogger, name=logger_helper().logger_name())
    help = providers.Singleton(app_helpers.Help, locale_paths, logger)
    locale_cfg_helper = providers.Singleton(app_helpers.Configuration, locale_paths, logger)
    cfg = providers.Configuration()
    profiles_cfg = providers.Singleton(dict)
    notifier = providers.Singleton(notificator.SingletonNotificationProvider)


container = Container()