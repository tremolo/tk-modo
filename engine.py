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
A Modo engine for Tank.

"""

import tank
import platform
import sys
import traceback
import time
import textwrap
import os

import lx
import shotgunsupport

CONSOLE_OUTPUT_WIDTH = 200

###############################################################################################
# methods to support the state when the engine cannot start up
# for example if a non-tank file is loaded in Modo

modo_log = open("c:/temp/modo_engine_log.txt", "a")

def log_msg(msg, type="INFO"):
    try:
        modo_log.write("{}:{}\n".format(type,msg))
        #for line in textwrap.wrap(msg, width=CONSOLE_OUTPUT_WIDTH):
        #    lx.out(line)
    except:
        pass
        
    #print msg

class SceneEventWatcher(object):
    """
    Encapsulates event handling for multiple scene events and routes them
    into a single callback.
    
    Specifying run_once=True in the constructor causes all events to be
    cleaned up after the first one has triggered
    """
    def __init__(self, cb_fn,  
                 scene_events=[],
                 run_once=False):
        #scene_events = [OpenMaya.MSceneMessage.kAfterOpen,  OpenMaya.MSceneMessage.kAfterSave, OpenMaya.MSceneMessage.kAfterNew]
        self.__message_ids = []
        self.__cb_fn = cb_fn
        self.__scene_events = scene_events
        self.__run_once=run_once

        # register scene event callbacks:                                
        self.start_watching()

    def start_watching(self):
        # if currently watching then stop:
        self.stop_watching()

        # TODO: implement
        return
        
        # now add callbacks to watch for some scene events:
        for ev in self.__scene_events:
            try:
                # msg_id = OpenMaya.MSceneMessage.addCallback(ev, SceneEventWatcher.__scene_event_callback, self);
                pass
            except Exception, e:
                # report warning...
                continue    
            self.__message_ids.append(msg_id);

        # create a callback that will be run when Maya 
        # exits so we can do some clean-up:
        # msg_id = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kMayaExiting, SceneEventWatcher.__maya_exiting_callback, self)
        self.__message_ids.append(msg_id);

    def stop_watching(self):
        for msg_id in self.__message_ids:
            pass
            #OpenMaya.MMessage.removeCallback(msg_id)
        self.__message_ids = []

    @staticmethod
    def __scene_event_callback(watcher):
        """
        Called on a scene event:
        """
        if watcher.__run_once:
            watcher.stop_watching()
        watcher.__cb_fn()

    @staticmethod
    def __maya_exiting_callback(watcher):
        """
        Called on Maya exit - should clean up any existing calbacks
        """
        watcher.stop_watching()

def refresh_engine(engine_name, prev_context, menu_name):
    """
    refresh the current engine
    """    
    #import rpdb2;rpdb2.start_embedded_debugger("12345")
    current_engine = tank.platform.current_engine()
    
    # first make sure that the disabled menu is reset, if it exists...
    #if pm.menu("ShotgunMenuDisabled", exists=True):
    #    pm.deleteUI("ShotgunMenuDisabled")
    
    # if the scene opened is actually a file->new, then maintain the current
    # context/engine.
    scene_name  = lxtd.current_scene().filename

    if not scene_name:
        return current_engine

    new_path = scene_name
    
    # this file could be in another project altogether, so create a new Tank
    # API instance.
    try:
        tk = tank.tank_from_path(new_path)
    except tank.TankError, e:
        # render menu
        shotgunsupport.add_disabled_menu()
        
        # (AD) - this leaves the engine running - is this correct?        
        return current_engine

    ctx = tk.context_from_path(new_path, prev_context)
    
    # if an engine is active right now and context is unchanged, no need to 
    # rebuild the same engine again!
    if current_engine is not None and ctx == prev_context:
        return current_engine
    
    if current_engine:
        current_engine.log_debug("Ready to switch to context because of scene event !")
        current_engine.log_debug("Prev context: %s" % prev_context)   
        current_engine.log_debug("New context: %s" % ctx)
        # tear down existing engine
        current_engine.destroy()
    
    # create new engine
    try:
        new_engine = tank.platform.start_engine(engine_name, tk, ctx)
    except tank.TankEngineInitError, e:
        log_msg("Shotgun: Engine cannot be started: %s" % e)
        
        # render menu
        shotgunsupport.add_disabled_menu()

        return None
    else:
        new_engine.log_debug("Launched new engine for context!")
        
    return new_engine
        
def on_scene_event_callback(engine_name, prev_context, menu_name):
    """
    Callback that's run whenever a scene is saved or opened.
    """
    new_engine = None
    try:        
        new_engine = refresh_engine(engine_name, prev_context, menu_name)
    except Exception, e:
        (exc_type, exc_value, exc_traceback) = sys.exc_info()
        message = ""
        message += "Message: Shotgun encountered a problem starting the Engine.\n"
        message += "Please contact toolkitsupport@shotgunsoftware.com\n\n"
        message += "Exception: %s - %s\n" % (exc_type, exc_value)
        message += "Traceback (most recent call last):\n"
        message += "\n".join( traceback.format_tb(exc_traceback))
        log_msg(message, type="ERROR") 
        new_engine = None
    
    if not new_engine:
        # don't have an engine but still want to watch for 
        # future scene events:
        cb_fn = lambda en=engine_name, pc=prev_context, mn=menu_name:on_scene_event_callback(en, pc, mn)
        SceneEventWatcher(cb_fn, run_once=True)



# for debug logging with time stamps
g_last_message_time = 0

class ModoEngine(tank.platform.Engine):
    
    ##########################################################################################
    # init and destroy
    
    def pre_app_init(self):
        """
        Runs after the engine is set up but before any apps have been initialized.
        """        
        # unicode characters returned by the shotgun api need to be converted
        # to display correctly in all of the app windows
        from tank.platform.qt import QtCore
        # tell QT to interpret C strings as utf-8
        utf8 = QtCore.QTextCodec.codecForName("utf-8")
        QtCore.QTextCodec.setCodecForCStrings(utf8)
        self.log_debug("set utf-8 codec for widget text")

    def init_engine(self):
        self.log_debug("%s: Initializing..." % self)
        
        
        # TODO: check Modo version info
        current_os = "linux64" #cmds.about(operatingSystem=True)
        if current_os not in ["mac", "win64", "linux64"]:
            raise tank.TankError("The current platform is not supported! Supported platforms "
                                 "are Mac, Linux 64 and Windows 64.")
 
        
        if self.context.project is None:
            # must have at least a project in the context to even start!
            raise tank.TankError("The engine needs at least a project in the context "
                                 "in order to start! Your context: %s" % self.context)

        self.log_debug("%s: Setting project..." % self)

        # Set the Modo project based on config
        self._set_project()
       
        # add qt paths and dlls
        self._init_pyside()

        # default menu name is Shotgun but this can be overriden
        # in the configuration to be Sgtk in case of conflicts
        self._menu_name = "Shotgun"
        if self.get_setting("use_sgtk_as_menu_name", False):
            self._menu_name = "Sgtk"
                  
        # need to watch some scene events in case the engine needs rebuilding:
        cb_fn = lambda en=self.instance_name, pc=self.context, mn=self._menu_name:on_scene_event_callback(en, pc, mn)
        self.__watcher = SceneEventWatcher(cb_fn)
        self.log_debug("Registered open and save callbacks.")
                
    def post_app_init(self):
        """
        Called when all apps have initialized
        """    
        self.log_debug("%s: post_app_init" % self)
        # detect if in batch mode
        if self.has_ui:

            #self._menu_handle = pm.menu("ShotgunMenu", label=self._menu_name, parent=pm.melGlobals["gMainWindow"])
            # create our menu handler
            tk_modo = self.import_module("tk_modo")
            self._menu_generator = tk_modo.MenuGenerator(self)
            # hook things up so that the menu is created every time it is clicked
            #self._menu_handle.postMenuCommand(self._menu_generator.create_menu)
    
    def destroy_engine(self):
        self.log_debug("%s: Destroying..." % self)
        
        # stop watching scene events:
        self.__watcher.stop_watching()
        
        # clean up UI:
        self._removeMenu()
    

    def _removeMenu(self):
        # TODO: remove menu. cleanup
        w = shotgunsupport.get_shotgun_widget()
        w.create_menu()

        return
        #try:
        #    lx.eval("select.attr " + menu_name)
        #    lx.eval("attr.delete")
        #except RuntimeError:
        #    pass


    def populate_shotgun_menu(self, menu):
        """
        Use the menu generator to populate the Shotgun menu
        """
        self._menu = menu
        self._menu_generator.create_menu(self._menu)
        
    # def createMenu(self, menubar):
    #     shotgun_menu = QtGui.QMenu("Shotgun")
    #     menubar.addMenu(shotgun_menu)
    #     self._menu_generator.create_menu(menubar)

    # def _createMenu(self, menu_name, commands=[]):

    #     # TODO: implement
    #     return

    #     self._removeMenu()

    #     lx.eval("attr.formCreate " + menu_name)
    #     for i, cmd in enumerate(commands):
    #         lx.eval("attr.addCommand {" + cmd.get('command', '') +"} " + str(i))
    #         lx.eval("attr.label {" + cmd.get('label', '') + "}")
        
    #     lx.eval("attr.catCreate "  + menu_name + " menubar section:tail")


    def _init_pyside(self):
        """
        Handles the pyside init
        """
        
        # first see if pyside is already present - in that case skip!
        try:
            from PySide import QtGui
        except:
            # fine, we don't expect pyside to be present just yet
            self.log_debug("PySide not detected - it will be added to the setup now...")
        else:
            # looks like pyside is already working! No need to do anything
            self.log_debug("PySide detected - the existing version will be used.")
            return
        
        
    def _get_dialog_parent(self):
        """
        Get the QWidget parent for all dialogs created through
        show_dialog & show_modal.
        """
        import shotgunsupport
        # this is valid as soon as the Qt interface is loaded
        return shotgunsupport.get_root_widget()
        
    @property
    def has_ui(self):
        return not lx.service.Platform().IsHeadless()    
    
    ##########################################################################################
    # logging
    
    def log_debug(self, msg):
        
        for l in textwrap.wrap(msg, CONSOLE_OUTPUT_WIDTH):
            log_msg(l, type="DEBUG")

        return

        global g_last_message_time
        
        # get the time stamps
        prev_time = g_last_message_time
        current_time = time.time()
        
        # update global counter
        g_last_message_time = current_time
        
        if self.get_setting("debug_logging", False):
            msg = "Shotgun Debug [%0.3fs]: %s" % ((current_time-prev_time), msg)
            for l in textwrap.wrap(msg, CONSOLE_OUTPUT_WIDTH):
                log_msg(l)
    
    def log_info(self, msg):
        #msg = "Shotgun: %s" % msg
        for l in textwrap.wrap(msg, CONSOLE_OUTPUT_WIDTH):
            log_msg(l, type="INFO")
        
    def log_warning(self, msg):
        #msg = "Shotgun: %s" % msg
        for l in textwrap.wrap(msg, CONSOLE_OUTPUT_WIDTH):
            log_msg(l, type="WARNING")
    
    def log_error(self, msg):
        #msg = "Shotgun: %s" % msg
        for l in textwrap.wrap(msg, CONSOLE_OUTPUT_WIDTH):
            log_msg(msg, type="ERROR")
    
    ##########################################################################################
    # scene and project management            
        
    def _set_project(self):
        """
        Set the modo project
        """
        setting = self.get_setting("template_project")
        if setting is None:
            return

        tmpl = self.tank.templates.get(setting)
        fields = self.context.as_template_fields(tmpl)
        proj_path = tmpl.apply_fields(fields)
        self.log_info("Setting Modo project to '%s'" % proj_path)        
        # TODO: to be implemented
    
