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


def bootstrap(engine_name, context, app_path, app_args):
    import tank.util
    # get the PYTHONPATH and store in MODO_PATH, Modo seems to clear PYTHONPATH
    # we use MODO_PATH later in module modoshotgunsupport
    os.environ["MODO_PATH"] = os.environ.get("PYTHONPATH", "")
    resource_path = os.path.realpath( os.path.join(os.path.dirname(__file__),"..","..", "resources") )
    #startup_path = os.path.dirname(__file__)
    tank.util.append_path_to_env_var("MODO_PATH", resource_path)

    return app_path, app_args


