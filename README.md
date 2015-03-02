# Documentation
This is the tk-modo engine to integrate Modo by The Foundry (http://www.thefoundry.co.uk/products/modo/)
with the project management software Shotgun by Autodesk (https://www.shotgunsoftware.com)

Parts of this work are based on Software by Shotgun Software Inc. (now part of Autodesk Inc.)


## Installation instructions

The installation description is for the project environment

From your local shotgun environment install the engine with the tank command:

```
tank install_engine project https://github.com/tremolo/tk-modo.git
```

Copy the contents of the install/engines/git/tk-modo.git/TK_MODO_VERSION/modo_support folder into your Modo User Scripts folder (for version 0.1.4):
```
cp -a install/engines/git/tk-modo.git/v0.1.4/modo_support/lxserv $HOME/.luxology/Scripts
```

### check that the configuration for tk-modo in env/project.yml is present
```
  tk-modo:
    apps:
      tk-multi-about: '@about'
      tk-multi-screeningroom: '@launch_screeningroom'
      tk-multi-workfiles: '@workfiles-launch-at-startup'
      tk-multi-publish:
        allow_taskless_publishes: true
        display_name: Publish Project
        expand_single_items: false
        hook_copy_file: default
        hook_post_publish: default
        hook_primary_pre_publish: default
        hook_primary_publish: default
        hook_scan_scene: default
        hook_secondary_pre_publish: default
        hook_secondary_publish: default
        hook_thumbnail: default
        location: {path: 'https://github.com/tremolo/tk-multi-publish.git', type: git, version: v0.6.7.1}
        primary_description: Publish and version up the selected Modo scene
        primary_display_name: Modo Publish
        primary_icon: icons/publish_hiero_main.png
        primary_publish_template: modo_project_publish
        primary_scene_item_type: work_file
        primary_tank_type: Modo Scene
        secondary_outputs: []
        template_work: modo_project_work
      tk-multi-screeningroom: '@launch_screeningroom'
      tk-multi-workfiles: '@workfiles-launch-at-startup'tung
    compatibility_dialog_min_version: 801
    debug_logging: false
    location: {path: 'https://github.com/tremolo/tk-modo.git', type: git, version: v0.1.4}
    menu_favourites:
    - {app_instance: tk-multi-workfiles, name: Shotgun File Manager...}
    template_project: null
    use_sgtk_as_menu_name: false
```

### Make sure you have defined the path to modo in your env/includes/app_launchers.yml config file

```
launch_modo:
  defer_keyword: ''
  engine: tk-modo
  extra: {}
  hook_app_launch: default
  hook_before_app_launch: default
  icon: '{target_engine}/icon_256.png'
  linux_args: ''
  linux_path: '@modo_linux'
  location: {name: tk-multi-launchapp, type: app_store, version: v0.6.2}
  mac_args: ''
  mac_path: '@modo_mac'
  menu_name: Launch Modo
  versions: []
  windows_args: ''
  windows_path: '@modo_windows'
 ```


### and in your env/includes/paths.yml config file:

```
# Modo
modo_windows: C:\Program Files\Luxology\modo\801_sp3\modo.exe
modo_linux: modo
modo_mac: /Applications/Modo.app
```


### Make sure the tk-multi-launchmodo command is defined  in every environment you are using for the tk-multi-launchapp  (env/project.yml and others)
```
tk-shell:
apps: {tk-multi-launch3dsmax: '@launch_3dsmax', tk-multi-launchhiero: '@launch_hiero', tk-multi-launchmodo: '@launch_modo',
  tk-multi-launchmaya: '@launch_maya', tk-multi-launchnuke: '@launch_nuke', tk-shotgun-launchphotoshop: '@launch_photoshop'}
debug_logging: false
location: {name: tk-shell, type: app_store, version: v0.4.1}
```


## Start Modo

You you should now be able to lauch Modo from Shotgun

```
tank launch_modo
```

For Modo without Qt support a floating window should open with Shotgun Logo,
use the menu in that window to open the Shotgun File Manager

For Modo with Qt support (on Linux and Modo 901) you can add the Shotgun panel into Modo by selecting the panel type "Application>Custom View>Shotgun",
use also the menu provided in the panel to open the Shotgun File Manage

* It may be necessary to select "Reload Shotgun" in the "Shotgun" menu of the panel to load the engine*
