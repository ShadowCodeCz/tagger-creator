import os.path
import argparse

from . import core
from . import app

import apphelpers

app_cfg_filename = "default.app"


def save_help(text):
    return text.replace("%", "%%")


def main():
    logger_helper = core.container.logger_helper()
    logger_helper.prepare_output_directory()
    logger_helper.configure()

    help = core.container.help()
    help.create_empty_help("app")
    help.read()
    app_help_text = help.get_help("app")

    locale_paths = core.container.locale_paths()
    cfg_helper = core.container.locale_cfg_helper()
    cfg_helper.create_cfg(app_cfg_filename,
                          {
                              "window": {
                                  "open_width": 590,
                                  "open_height": 750
                              },
                              "profiles_config": "C:\\Users\\sedaj\\tagger.core\\cfg\\cfg.json"
                          })

    description = app_help_text

    cfg = cfg_helper.read_file(app_cfg_filename)

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers()

    app_parser = subparsers.add_parser('app')
    app_parser.add_argument("-c", "--configuration", default=locale_paths.configuration_file(app_cfg_filename), help=str(locale_paths.configuration_file(app_cfg_filename)))
    app_parser.set_defaults(func=app.ApplicationCLI.run)

    arguments = parser.parse_args()
    arguments.func(arguments)