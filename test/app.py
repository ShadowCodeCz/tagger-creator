import os

import taggercreator
import argparse

taggercreator.app.ApplicationCLI.run(argparse.Namespace(**{
    "configuration": "./debug.configuration.json",
}))

