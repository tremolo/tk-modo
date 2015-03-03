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

import sys
import os

def setup_pyside_distribution(resource_path):
    if sys.platform != "win32":
        return
    
    # check if PySide has been extracted
    if not os.path.isdir(os.path.join(resource_path, "PySide")):
        pyside_distribution = os.path.join(resource_path, "PySide_1_2_2__Qt4_8_6.zip")
        if os.path.exists(pyside_distribution):
            # extract PySide distribution from zip file for Windows platform
            import zipfile
            with zipfile.ZipFile(pyside_distribution, "r") as z:
                z.extractall(resource_path)
        else:
            print "Can not locate PySide distribution.  Make sure PySide is available for your platform"


def bootstrap(engine_name, context, app_path, app_args):
    import tank.util
    # get the PYTHONPATH and store in MODO_PATH, Modo seems to clear PYTHONPATH
    # we use MODO_PATH later in module modoshotgunsupport
    os.environ["MODO_PATH"] = os.environ.get("PYTHONPATH", "")
    resource_path = os.path.realpath( os.path.join(os.path.dirname(__file__),"..","..", "resources") )
    setup_pyside_distribution(resource_path)
    tank.util.append_path_to_env_var("MODO_PATH", resource_path)

    return app_path, app_args


