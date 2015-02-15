#   Copyright (c) 2001-2014, The Foundry Visionmongers Ltd.
#   All Rights Reserved. Patents granted and pending.
#

##
## W:\WG\Shotgun_Configs\RTS_Master_develop\tank.bat --debug  Task @28197 launch_modo

import sys
import os

#_logfile = open(r"C:\temp\modoengine.txt", "a")

def log(msg,type="INFO"):
    try:
        #import lx
        #lx.out(msg)
        #_logfile.write(msg+"\n")
        #_logfile.flush()
        print(msg)
    except:
        pass

for path in os.environ.get('MODO_PATH','').split(os.pathsep):
    if path not in sys.path:
        sys.path.append(path)
        log("appended path '{0}' to sys.path".format(path))
            

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
EXTRA_MODULES_PATH = os.path.realpath(os.path.join(CURRENT_PATH, "..", "..", "modules"))

if EXTRA_MODULES_PATH not in sys.path:
    log("Adding EXTRA MODULES PATH")
    sys.path.append(EXTRA_MODULES_PATH)
    import distutils.version

try:
    import lx
    import lxu
    import lxifc
    import lxtd
    import lxtd.constants
    MODO_AVAILABLE = True
    log("MODO startup")
except ImportError:
    import traceback;traceback.print_exc()
    MODO_AVAILABLE = False
    log("MODO import fail")


from PySide import QtGui, QtCore

class ModoApplication(QtGui.QApplication):
    def __init__(self,  *args):
        super(ModoApplication, self).__init__(  *args)

    def notify(self, receiver, event):
        if  event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() < 1000:
                # only handle printable characters
                is_shift_pressed = self.keyboardModifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier

                text = QtGui.QKeySequence(event.key()).toString()
                text = text.upper() if is_shift_pressed else text.lower()
                
                # QKeyEvent.text() does not work properly here
                # copy the event data and use the altered text
                mod_event  = QtGui.QKeyEvent.createExtendedKeyEvent(event.type(), event.key(), event.modifiers(),
                                                                    event.nativeScanCode(), event.nativeVirtualKey(),
                                                                    event.nativeModifiers(), text=text )
                # handle modified event
                return super(ModoApplication, self).notify(receiver, mod_event)


        return super(ModoApplication, self).notify(receiver, event)    

SHOTGUN_LOCALS = {}

_shotgun_parent = None
_shotgun_panel = None

def modo_version():
    platform = lx.service.Platform()
    return platform.AppVersion()

def no_embedded_qt_mode():
    return (modo_version() == 801) and (sys.platform == "win32")


def get_scene_filename():
    return lxtd.current_scene().filename or ""


def reset_scene():
    close_all_scenes()
    lx.eval('scene.new')


def save_scene():
    try:
        lx.eval('scene.save')
    except RuntimeError as e:
        if "Scene has not been changed" in e.message:
            # this is not really an error, accept silently
            return
        raise


def save_scene_as(filename):
    lx.eval("scene.saveAs {%s}" % filename)


def load_file(filename):
    lx.eval("scene.open {%s}" % filename)


def get_meshes():
    scene = lxtd.scene.current_scene()
    return  scene.meshes


def close_all_scenes():
    lx.eval("scene.closeAll")


def get_root_widget():
    return _shotgun_parent


def get_shotgun_widget():
    return _shotgun_panel


def get_references():

    scene_svc = lx.service.Scene()
    scene = lxu.select.SceneSelection().current()
     
    # we need to create a null terminated list of item type IDs and wrap it as a
    # storage object that we can pass to the lx.object.Scene.ItemCountByTypes &
    # lx.object.Scene.ItemByIndexByTypes methods later.
    itype_ids = [scene_svc.ItemTypeByIndex(x) for x in xrange(scene_svc.ItemTypeCount())]
    itype_ids.append(0)
    item_types = lx.object.storage()
    item_types.setType('i')
    item_types.set(itype_ids)
     
    # build a list of paths for referenced items in the scene
    refpaths = set()
    for x in xrange(scene.ItemCountByTypes(item_types)):
        try:
            refpaths.add(scene.ItemByIndexByTypes(item_types, x).Reference().Context().Filename())
        except LookupError:
            pass

    return refpaths

def item_channels(item):
    return dict([(c,item.get_channel(c)) for c in item.item.ChannelList()])
    
def all_item_channels(itemtype):
    scene = lxtd.current_scene()
    return [(item,item_channels(item)) for item in scene.items(itemtype)]

def item_types():
    return {lxtd.constants.SCENE_SVC.ItemTypeName(i):i for i in range(lxtd.constants.SCENE_SVC.ItemTypeCount())}



def add_disabled_menu():
    if not _shotgun_panel:
        return

    menu = _shotgun_panel.get_menu()
    if not menu:
        return

    disabled_title = "Shotgun is Disabled"
    disabled_menu_item = [item for item in menu.children() if item.title() == disabled_title]
    if not disabled_menu_item:
        menu.addAction(disabled_title, self.shotgun_disabled)


def remove_disabled_menu():
    if not _shotgun_panel:
        return

    menu = _shotgun_panel.get_menu()
    if not menu:
        return
    disabled_title = "Shotgun is Disabled"
    for item in menu.children():
        if item.title() == disabled_title:
            menu.removeAction(item)
    
if MODO_AVAILABLE:
    SessionListenerBase = lxifc.SessionListener
    ModoSceneListenerBase   = lxifc.SceneItemListener
else:
    SessionListenerBase = object
    ModoSceneListenerBase = object



class ModoSessionListener(SessionListenerBase):
    def __init__(self):
        self.callbacks = {}

    def add_callback(self, topic,cb):
        self.callbacks.setdefault(topic,[]).append(cb)

    def remove_callback(self, topic,cb):
        callbacks =  self.callbacks.setdefault(topic,[])
        if cb in callbacks:
            callbacks.remove(cb)

    def sesl_FirstWindowOpening(self):
        lx.out('sesl_FirstWindowOpening(self):')
    def sesl_BeforeStartupCommands(self):
        lx.out('sesl_BeforeStartupCommands(self):')
    def sesl_SystemReady(self):
        lx.out('sesl_SystemReady(self):')
    def sesl_CheckQuitUI(self,quitWasAborted):
        lx.out('sesl_CheckQuitUI(self,quitWasAborted):')
    def sesl_QuittingUI(self):
        lx.out('sesl_QuittingUI(self):')
    def sesl_LastWindowClosed(self):
        lx.out('sesl_LastWindowClosed(self):')
    def sesl_ShuttingDown(self):
        lx.out('sesl_ShuttingDown(self):')



class ModoSceneListener(ModoSceneListenerBase):
    def __init__(self):
        self.callbacks = {}


    def add_callback(self, topic,cb):
        self.callbacks.setdefault(topic,[]).append(cb)

    def remove_callback(self, topic,cb):
        callbacks =  self.callbacks.setdefault(topic,[])
        if cb in callbacks:
            callbacks.remove(cb)

    def _handle_callback(self,callbackname, *args,**kwds):
        for cb in self.callbacks.get(callbackname,[]):
            try:
                cb(*args,**kwds)
            except:
                pass

    def sil_SceneCreate(self,scene):
        self._handle_callback('sil_SceneCreate', scene)

    def sil_SceneDestroy(self,scene):
        self._handle_callback('sil_SceneDestroy', scene)

    def sil_SceneFilename(self,scene,filename):
        self._handle_callback('sil_SceneFilename', scene,filename)

    def sil_SceneClear(self,scene):
        self._handle_callback('sil_SceneClear', scene)
    
    def sil_ItemPreChange(self,scene):
        self._handle_callback('sil_ItemPreChange', scene)

    def sil_ItemPostDelete(self,scene):
        self._handle_callback('sil_ItemPostDelete', scene)

    def sil_ItemAdd(self,item):
        self._handle_callback('sil_ItemAdd', item)

    def sil_ItemRemove(self,item):
        self._handle_callback('sil_ItemRemove', item)

    def sil_ItemParent(self,item):
        self._handle_callback('sil_ItemParent', item)

    def sil_ItemChild(self,item):
        self._handle_callback('sil_ItemChild', item)

    def sil_ItemAddChannel(self,item):
        self._handle_callback('sil_ItemAddChannel', item)

    def sil_ItemLocal(self,item):
        self._handle_callback('sil_ItemLocal', item)

    def sil_ItemName(self,item):
        self._handle_callback('sil_ItemName', item)

    def sil_ItemSource(self,item):
        self._handle_callback('sil_ItemSource', item)

    def sil_ItemPackage(self,item):
        self._handle_callback('sil_ItemPackage', item)

    def sil_ChannelValue(self,action,item,index):
        self._handle_callback('sil_ChannelValue', action,item,index)

    def sil_LinkAdd(self,graph,itemFrom,itemTo):
        self._handle_callback('sil_LinkAdd', graph,itemFrom,itemTo)

    def sil_LinkRemBefore(self,graph,itemFrom,itemTo):
        self._handle_callback('sil_LinkRemBefore', graph,itemFrom,itemTo)

    def sil_LinkRemAfter(self,graph,itemFrom,itemTo):
        self._handle_callback('sil_LinkRemAfter', graph,itemFrom,itemTo)

    def sil_LinkSet(self,graph,itemFrom,itemTo):
        self._handle_callback('sil_LinkSet', graph,itemFrom,itemTo)

    def sil_ChanLinkAdd(self,graph,itemFrom,chanFrom,itemTo,chanTo):
        self._handle_callback('sil_ChanLinkAdd', graph,itemFrom,chanFrom,itemTo,chanTo)

    def sil_ChanLinkRemBefore(self,graph,itemFrom,chanFrom,itemTo,chanTo):
        self._handle_callback('sil_ChanLinkRemBefore', graph,itemFrom,chanFrom,itemTo,chanTo)

    def sil_ChanLinkRemAfter(self,graph,itemFrom,chanFrom,itemTo,chanTo):
        self._handle_callback('sil_ItemParent', graph,itemFrom,chanFrom,itemTo,chanTo)

    def sil_ChanLinkSet(self,graph,itemFrom,chanFrom,itemTo,chanTo):
        self._handle_callback('sil_ChanLinkSet', graph,itemFrom,chanFrom,itemTo,chanTo)

    def sil_ItemTag(self,item):
        self._handle_callback('sil_ItemTag', item)


class EventListener(object):
    """Listen for certain Modo events (scene and session)"""
    def __init__(self):

        if MODO_AVAILABLE:
            self.listener_svc = lx.service.Listener()
            self.scene = ModoSceneListener()
            self.session = ModoSessionListener()

    def register(self):
        if not MODO_AVAILABLE:
            self.listener_svc.AddListener(self.scene)
            self.listener_svc.AddListener(self.session)


    def unregister(self):
        if not MODO_AVAILABLE:
            self.listener_svc.RemoveListener(self.scene)
            self.listener_svc.RemoveListener(self.session)

event_listener = EventListener()


class ShotgunWidget(QtGui.QWidget):
    def __init__(self, parent=None):        
        super(ShotgunWidget, self).__init__(parent)
        #windowflags =  (QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint) | QtCore.Qt.WindowStaysOnTopHint
        windowflags = (QtCore.Qt.WindowFlags() & QtCore.Qt.Popup & QtCore.Qt.WindowType_Mask) | QtCore.Qt.WindowStaysOnTopHint
        #windowflags = windowflags & ~(QtCore.Qt.WindowMinimizeButtonHint|QtCore.Qt.WindowMaximizeButtonHint|QtCore.Qt.WindowCloseButtonHint)
        self.setWindowFlags(windowflags)
        log("creating Shotgun widget")
        self.lbl_shotgun = QtGui.QLabel("Hello From Shotgun")
        shotgun_logo = QtGui.QImage(os.path.join(os.path.dirname(os.path.realpath(__file__)), "./shotgun.png"))
        self.lbl_shotgun.setPixmap(QtGui.QPixmap.fromImage(shotgun_logo.scaled(128,128,QtCore.Qt.KeepAspectRatio)))

        self.menubar = QtGui.QMenuBar()
        self.menu = self.menubar.addMenu("Shotgun")
        self.create_menu()
        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.menubar)
        self.layout.addWidget(self.lbl_shotgun)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.menubar.setFixedHeight(20)
        self.setLayout(self.layout)
        self.resize(128,128)
        self.mpos = None

    def mousePressEvent(self, event):
        self.mpos = event.pos()

    def mouseMoveEvent(self, event):
        if not self.mpos: return
        if (event.buttons() & QtCore.Qt.LeftButton):
            diff = event.pos() - self.mpos
            newpos = self.pos() + diff
            self.move(newpos)

    def create_menu(self):
        self.menu.clear()        
        self.menu.addAction("Reload Shotgun", self.reload_shotgun)


    def shotgun_disabled(self):
        msg = ("Shotgun integration is disabled because it cannot recognize "
               "the currently opened file.  Try opening another file or "
               "restarting Modo.")

        QtGui.QMessageBox.information(None, "Sgtk is disabled", msg)

    def add_disabled_menu(self):
        self.menu.addAction("Shotgun is disabled!", self.shotgun_disabled)

    def reload_shotgun(self, *args):
        log("reloading shotgun")
        try:
            #import rpdb2;rpdb2.start_embedded_debugger("12345")
            import init_tank
            reload(init_tank)
            
            init_tank.bootstrap_tank()

            import sgtk
            engine = sgtk.platform.current_engine()
            if engine:
                # ask the engine to build the menu:
                self.create_menu()
                engine.populate_shotgun_menu(self.menu)
            else:
                self.add_disabled_menu()
        except:
            import traceback
            traceback.print_exc()

    def get_menu(self):
        return self.menu

if MODO_AVAILABLE:
    class ShotgunCmd(lxu.command.BasicCommand):
        def __init__(self):
            lxu.command.BasicCommand.__init__(self)
            self.dyna_Add('command',  lx.symbol.sTYPE_STRING)      # 0
            #self.basic_SetFlags(1, lx.symbol.fCMDARG_OPTIONAL)
            
        def basic_Execute(self, msg, flags):
            command = self.dyna_String(0)
            try:
                exec command in SHOTGUN_LOCALS, SHOTGUN_LOCALS
            except:
                lx.out('SHOTGUN ERROR : {0} {1} {2}'.format(command, msg,flags))
                raise


    class ShotgunStartupCmd(lxu.command.BasicCommand):
        def __init__(self):
            lxu.command.BasicCommand.__init__(self)
            self.dyna_Add('command',  lx.symbol.sTYPE_STRING)      # 0
            #self.basic_SetFlags(1, lx.symbol.fCMDARG_OPTIONAL)
            
        def basic_Execute(self, msg, flags):
            command = self.dyna_String(0)
            #print 1/0
            try:
                lx.out('SHOTGUN Startup '+ command)
            except:
                lx.out('SHOTGUN ERROR : {0} {1} {2}'.format(command, msg,flags))
                raise


    class lxShotgunServer(lxifc.CustomView):

        def customview_Init(self, pane):
            global _shotgun_parent
            global _shotgun_panel

            log("customview_Init")

            if pane == None:
                return False

            custPane = lx.object.CustomPane(pane)

            if not custPane.test():
                log("unable to create custom pane")
                return False

            # get the parent object
            parent = custPane.GetParent()

            # convert to PySide QWidget
            p = lx.getQWidget(parent)


            # Check that it suceeds
            if p != None:

                log("UI INIT")

                _shotgun_parent = p

                shotgunWidget  = ShotgunWidget(p)
                _shotgun_panel = shotgunWidget

                layout = QtGui.QVBoxLayout()
                layout.addWidget(shotgunWidget)
                layout.setContentsMargins(2,2,2,2)
                p.setLayout(layout)
                
                log("init_tank.bootstrap_tank")
                try:
                    shotgunWidget.reload_shotgun()
                    log("bootstrap completed")
                except:
                    log("bootstrap failed")
                    lx.out("can not import shotgun startup script")

                return True


            return False

        def customview_StoreState(self, pane):
            custpane = lx.object.CustomPane(pane)
            # TODO: what state needs to be saved ?


        def customview_RestoreState(self, pane):
            pass
            #custpane = lx.object.CustomPane(pane)
            # TODO: what state needs to be saved ?


        def customview_Cleanup(self, pane):
            try:
                self.customview_StoreState(pane)
            except RuntimeError, e:
                if e.message == "Internal C++ object (ShotgunWidget) already deleted.":
                    if hasattr(lx, "shotgun_widget"):
                        lx.shotgun_widget.destroy()


    log("blessing shotgun.eval")
    lx.bless(ShotgunCmd, "shotgun.eval")
    log("blessing shotgun.startup")
    lx.bless(ShotgunStartupCmd, "shotgun.startup")
    tags = {}
    try:
        tags = { lx.symbol.sCUSTOMVIEW_TYPE: "vpeditors SCED shotgun @shotgun.view@Shotgun@", }
    except:
        pass


    event_listener.register()

    if no_embedded_qt_mode():
        app = ModoApplication([])
        _shotgun_panel = ShotgunWidget()
        _shotgun_panel.show()
        _shotgun_panel.raise_()
    else:
        if( not lx.service.Platform().IsHeadless() ):
           lx.bless(lxShotgunServer, "Shotgun", tags)



def test():
    global _modo_app
    _modo_app = ModoApplication(sys.argv)
    w = ShotgunWidget()
    w.show()
    _modo_app.exec_()

if __name__ == '__main__':
    test()
