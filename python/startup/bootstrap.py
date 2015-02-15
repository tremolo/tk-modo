# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
This file is loaded automatically by Modo at startup
It sets up the tank context and prepares the Tank Modo engine.
"""


import os
import lx

def log_msg(msg):
    lx.out(msg)


def bootstrap(engine_name, context, app_path, app_args):
    import tank.util
    # get the PYTHONPATH and store in MODO_PATH, Modo seems to clear PYTHONPATH
    # we use MODO_PATH later in module shotgunsupport
    os.environ["MODO_PATH"] = os.environ.get("PYTHONPATH", "")
    #startup_path = os.path.abspath(os.path.join(self._get_app_specific_path("modo"), "startup"))
    startup_path = os.path.dirname(__file__)
    tank.util.append_path_to_env_var("MODO_PATH", startup_path)

    return app_path, app_args


