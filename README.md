# PieMenu
PieMenu widget for FreeCAD 

Quick customizable menus for FreeCAD.

### Version 1.8 new features:
Add ability to export/import PieMenu settings.

![Capture d’écran (231)](https://github.com/user-attachments/assets/796c8694-5d5f-471f-8d68-06bb63b7053f)


# Presentation: PieMenu is a customizable menu, providing quick access to FreeCAD tools via keyboard shortcuts. You can choose from multiple shapes, themes, customize tools and shortcuts, and much more... 

Warning: PieMenu is in development, bugs may still exist. It is necessary to backup your configuration files before any PieMenu installation or update to be able to restore them in case of issues. 

You can choose between many shapes :

![Capture d’écran (65)](https://github.com/Grubuntu/PieMenu-Improved/assets/56045316/44302640-bb98-4612-b951-0e999fa280c6) 
![Capture d’écran (66)](https://github.com/Grubuntu/PieMenu-Improved/assets/56045316/e2788ed3-ceec-4871-9142-afd9a31d34e5)



'Sketcher' PieMenu is a special PieMenu, which is called when you edit a sketch in Sketcher.

![Capture d’écran (2)](https://github.com/Grubuntu/PieMenu-Improved/assets/56045316/1a449eda-b29a-40de-b06d-b55f672a4aa2)


Choose between many themes :

![Capture d’écran (10)](https://github.com/Grubuntu/PieMenu-Improved/assets/56045316/30f21f77-24ad-4491-bc75-11538d2ab527)
![Capture d’écran (19)](https://github.com/Grubuntu/PieMenu-Improved/assets/56045316/5339d57d-785b-4e27-a410-c79677c3d8b1)
![Capture d’écran (48)](https://github.com/Grubuntu/PieMenu-Improved/assets/56045316/e87f5706-4642-46b1-aaab-e1e17b9ede20)


Create custom PieMenus by adding desired commands through preferences :
Select size, shape, tools, individual shortcut for each PieMenu and/or a global shortcut to open a default PieMenu.


### Installation
PieMenu can be installed via the FreeCAD add-on manager. Once installed, you should find a new "Accessories" menu in the FreeCAD menu bar. 

![image](https://github.com/Grubuntu/PieMenu/assets/56045316/c992fb79-9399-4174-9827-ae3de41b7025)

Or just add all files in a PieMenu directory in your FreeCAD Mod directory.
![Capture d’écran (21)](https://github.com/Grubuntu/PieMenu-Improved/assets/56045316/a0fbcb3e-a5c5-4687-93ed-5b734e1ef63a)

(Windows) Or in  %AppData%\FreeCAD\Mod\

![Capture d’écran (20)](https://github.com/Grubuntu/PieMenu-Improved/assets/56045316/2acee710-2cee-42f3-ab3a-4e10c94d27af)

Install path for FreeCAD modules depends on the operating system used.  
To find where is the user's application data directory enter next command on FreeCAD Python console.

```python
App.getUserAppDataDir()
```

##### Examples:

Linux:

`/home/user/.local/share/FreeCAD/Mod/PieMenu/InitGui.py`

macOS:

`/Users/user_name/Library/Preferences/FreeCAD/Mod/PieMenu/InitGui.py`

Windows:

`C:\Users\user_name\AppData\Roaming\FreeCAD\Mod\PieMenu\InitGui.py`

### Discussion
FreeCAD forum thread: https://forum.freecad.org/viewtopic.php?t=84101


Thanks to all the work done by mdkus, triplus, looo, microelly.

### Usage
Press the Tab key on the keyboard to invoke PieMenu or set shortcut via Accessories Menu



### Definitions: 

A *PieMenu* is a set of tools grouped within a menu to create a shortcut bar accessible via a keyboard shortcut.

A *ToolBar* is a set of existing shortcuts in FreeCAD, containing a set of tools from a workbench.

*Context* Mode: A special activation mode that takes into account the geometry selected by the user to determine which PieMenu to activate based on the settings.

*Global shortcut*: General shortcut assigned to PieMenu to open the default PieMenu. 

*Individual shortcut*: Shortcut assigned to a particular PieMenu.

## 1 – First launch  :

It may be necessary to restart FreeCAD after installation and after the initial activation of PieMenu to ensure that the configuration is set up correctly.

By default, the global shortcut to activate PieMenu is the 'TAB' key. However, if this does not work or if you wish to change it, you can access the Preferences via the "Accessories" menu > "General Preferences" tab > Global Shortcut.

You can assign a simple shortcut (e.g., a single key like 'A'), a composite shortcut (e.g., 'CTRL + Q'), or multi-key shortcuts (e.g., 'F, F').

## 2 – Create/modify a PieMenu :

In case of a fresh installation, PieMenu will create 3 PieMenus (View, PartDesign, and Sketcher) with some common tools. 
To create or modify other PieMenus, simply go to the "Preferences" (*QuickMenu* > Preferences or Accessories Menu > PieMenu Preferences).

The *QuickMenu* is the contextual menu displayed when clicking on the integrated button in the PieMenu (option to activate if needed in the 'Preferences'). 

![Capture d’écran (180) quickmenu](https://github.com/Grubuntu/PieMenu/assets/56045316/5008258c-eb9f-4fb7-9a5c-ee55873173dc)


The QuickMenu allows for quickly adjusting certain settings. If the QuickMenu is not visible, it must be enabled in the "Preferences" by activating the "Show QuickMenu" option.

![Capture d’écran (177)](https://github.com/Grubuntu/PieMenu/assets/56045316/fef43f63-8ab5-4d91-9b64-32c4d2bf47e0)


### 1) PieMenu Tab:

Create a new PieMenu by clicking on the '+' button, name it, and validate. It will now be visible in the dropdown list of PieMenus.
Modify and adjust available settings (settings may vary depending on the PieMenu configuration):

    
    • Menu size: adjusts the size of the menu
    
    • Button size: adjusts the size of the buttons (Note: maximum size depends on the menu size)
    
    • Shape: multiple shapes are available

    • Trigger Mode : Choose the activation mode: 'On press' or 'On hover' of the mouse for this PieMenu
    
    • Set the hover activation delay: to avoid triggering too quickly when passing over multiple commands, it is necessary to set a sufficient delay.
    
    • Show command names: some shapes allow displaying command names
    
    • Number of rows and columns: for shapes allowing a layout in rows and/or columns
    
    • Icon spacing: adjusts the space between buttons.
    
    
### 2) Tools Tab:

Check the desired tools to add them to your PieMenu tool list.
You can move or delete tools using the buttons located below the tools list.
Tip: You can search for tools by their name in the search bar.

### 3) Context Tab: (Attention, this feature is not fully functional, there may be bugs)

Context allows activating a specific PieMenu based on the geometry selected by the user. For example, when the user selects a face in the 3D model, one might want a PieMenu for creating a 'New Sketch' to open. This is possible with the Context mode.


Example: In the example below, a context is assigned to the "Fillet Chamfer" PieMenu which contains tools such as Measure, Delete, Fillet, Chamfer, WireFrame, and As Is. 


![Capture d’écran (110)](https://github.com/Grubuntu/PieMenu/assets/56045316/a3bd71fe-7461-4e65-a38a-0ff23ae43daa)

![image](https://github.com/Grubuntu/PieMenu/assets/56045316/96975363-34cf-4953-b6f0-518199d843c8)

We enable the context mode for this PieMenu by checking the "Enable" box and set the selections as desired: here, we want the "Fillet Chamfer" PieMenu to activate when the user's selection contains at least one edge or more. With this configuration, when the user has selected at least one edge of the 3D geometry, the "Fillet Chamfer" PieMenu will open upon pressing the global shortcut. 

You can enable/disable the context mode in the global preferences or via the QuickMenu by checking/unchecking "Context". 

Important note: The "Context" mode takes priority over all other modes. Therefore, when the selection conditions are met, this PieMenu will be activated by the global shortcut even if another PieMenu is set as default via the QuickMenu  or via the association of a Workbench. Therefore, it is important to activate the context mode judiciously. 

![Capture d’écran (180)](https://github.com/Grubuntu/PieMenu/assets/56045316/b999ee58-b270-4e20-8195-953b52e69014)

![Capture d’écran (177)](https://github.com/Grubuntu/PieMenu/assets/56045316/cdaa6f6a-e3f8-465d-ae7b-f2d8d3c821ac)



### 4) Global settings tab :

Here, you can:

    • Select the theme style
    
    • Enable or disable the QuickMenu (context menu)
    
    • Enable or disable the Context mode (also available in the QuickMenu).
    
    • Assign the global shortcut.

    • Enable or disable the toggle mode for the global shortcut.
    
![Capture d’écran (177)](https://github.com/Grubuntu/PieMenu/assets/56045316/19149d70-e511-414f-a589-e3edf4c63a35)

![Capture d’écran (113)](https://github.com/Grubuntu/PieMenu/assets/56045316/8a06e5c2-c67b-4d89-aea3-55f22d472195)

Hover Activation Delay: For example, in the case of the "TableTop" PieMenu shape, to reach the "Fillet" tool, one must hover over the "Pad" or "New Sketch" tool. 
To avoid triggering these tools when hovering over them with the mouse, a hover activation delay is set (e.g., 200ms). 
PieMenu will wait for the mouse to hover over the "Fillet" button for 200ms before executing the command. 

## 3 – Advanced settings :

Several settings are available to define the PieMenu activated by the global shortcut: 

1) ToolBar:
You can define a default ToolBar that will be activated by the global shortcut:
    • Via the QuickMenu > Menu ToolBar
    • Select one of the desired shortcut bars and click on "Show".
   
   ![image](https://github.com/Grubuntu/PieMenu/assets/56045316/21c39e63-83f6-48e3-9cf7-c4ca2a37d644)
   ![image](https://github.com/Grubuntu/PieMenu/assets/56045316/975f20c3-3665-4998-9317-920a600b897d)

This shortcut bar will now be activated by default by the global shortcut. This method is convenient if you want to use an existing shortcut bar from FreeCAD. By clicking on "Save", you save this bar in the list of existing PieMenus.

2) Default PieMenu:

You can define a default PieMenu from the existing PieMenus:
Open the QuickMenu

![Capture d’écran (180) defaut](https://github.com/Grubuntu/PieMenu/assets/56045316/d4c15cc3-7729-47e7-bb44-a3bc3b4631d2)

Or in globals settings

![Capture d’écran (176)](https://github.com/Grubuntu/PieMenu/assets/56045316/13144eb9-5b2d-4561-9414-3460b342af2f)

Click on "PieMenu" to expand the menu and select the desired PieMenu: this will now be activated by default by the global shortcut (a checkmark is visible in front of the default PieMenu, if no checkmark is visible, it means that a ToolBar is currently active by default.

3) Workbench associated:

You can associate a workbench with a menu, it will be opened when the workbench is active and when you press the global shortcut 

4) Individual Shortcut:

You can assign an individual shortcut to each PieMenu:

Each PieMenu can have its own individual shortcut. Simply go to the preferences and assign a shortcut to a PieMenu.

![image](https://github.com/Grubuntu/PieMenu/assets/56045316/42f19075-4e4c-4bb0-9229-5b668d190eab)

This shortcut allows activating the PieMenu regardless of the active Workbench or context.

**Known limitation: The use of multi-key shortcuts can sometimes conflict with single-key shortcuts.
For example, if you assign the single-key shortcut 'F' to one PieMenu and the multi-key shortcut 'F, D' to another PieMenu, there will be a conflict because PieMenu will always capture the single-key shortcut 'F' and will not be able to interpret the multi-key shortcut. Therefore, it is important to be careful with the different shortcuts assigned.**


## 4 - Shortcut Bar Priority:

PieMenus will be activated in order of priority when the global shortcut is pressed. The priority order is as follows: 

1 - Active Context 

2 - Active ToolBar 

3 - Associated Workbench

4 - Default PieMenu


If the "Context" mode is active and the selection conditions are met, then the PieMenu corresponding to the "Context" will be displayed. 

Otherwise, if a ToolBar is active (via the QuickMenu), then that ToolBar is displayed. 

OtherWise, if a Workbench is associated to the PieMenu, then the associated PieMenu is displayed.

Otherwise, the default PieMenu (checked in the QuickMenu) will be displayed.

## 5 - Quick Menu Spinbox:

The quick menu spinbox is displayed when pressing the global shortcut during the editing of certain features in the PartDesign workbench: Pad, Pocket, Chamfer, Fillet, Revolution, Groove.

![Capture d’écran (181)](https://github.com/Grubuntu/PieMenu/assets/56045316/9f19cae0-94fb-4998-a311-420ee0539ca1)

It allows quick access to modifying the main value of the function (Length, Depth, Angle, Size, etc.) as well as quick access to certain parameters of the Pad and Pocket functions: 'Through all', 'Symmetric to plane', and 'Reversed'.
The fast spinbox menu includes units and some capabilities for making calculations and expressions. You can quickly validate either by pressing the 'Enter' or 'Return' key, or by clicking the 'Validation' button.

## Other settings :

We can set the trigger mode (Hover/Press) individually for each PieMenu.

![Capture d’écran (179)](https://github.com/Grubuntu/PieMenu/assets/56045316/c22fc499-778a-4418-916a-0868da69ddb8)

Toggle mode for global shortcut : Pressing the global shortcut can toggle the PieMenu display.

![Capture d’écran (177)](https://github.com/Grubuntu/PieMenu/assets/56045316/34b6f579-074c-49e3-bd43-684a35ac9147)

## Since version 1.4, you need to link the Sketcher workbench to your "Sketcher" PieMenu to keep your sketching PieMenu opening automatically, see below.
We can associate a workbench for each PieMenu : When you associate a workbench with a menu, it will be opened when you press the global shortcut.

In the example below, the Draft workbench is associated with the "Snapping Tools" PieMenu: when the "Draft" workbench is active, the "Snapping Tools" PieMenu will open when the global shortcut key is pressed.
> Open from menu Accessories->Pie menu settings.

![Capture d’écran (178)](https://github.com/Grubuntu/PieMenu/assets/56045316/b24a458e-2e67-4758-906a-238ff8ce08d7)


In this way, you can associate a specific PieMenu for each Workbench. This is very useful, for example, for the Sketcher workbench, where you can associate a PieMenu with the tools specific to the Sketcher : 

![Capture d’écran (179)](https://github.com/Grubuntu/PieMenu/assets/56045316/52a0a995-5161-4bb6-8da7-4bd47972f20a)

## Tools shortcuts keys
Quickly launch a tool with one key shortcut when a PieMenu is displayed

![Capture d’écran (173)](https://github.com/Grubuntu/PieMenu/assets/56045316/88752663-491a-47f4-9a5b-526b90606f86)

You can enable them in the settings (from menu Accessories->Pie menu settings):
Enable and display them (or only enable them without displaying). You can set the font size.

![Capture d’écran (175)](https://github.com/Grubuntu/PieMenu/assets/56045316/fe63f92f-84ea-49c7-8c2c-f805434f8614)

### Version 1.6 new features :

- Ability to set icon for each PieMenu (FreeCAD must be restarted for the new icon to take effect correctly.):
  
![Capture d’écran (200)](https://github.com/Grubuntu/PieMenu/assets/56045316/0bab416c-444a-41e5-9302-0a6d14c344d9)

- Ability to add nested PieMenu : a PieMenu can now call another PieMenu:

![Capture d’écran (201)](https://github.com/Grubuntu/PieMenu/assets/56045316/9082b6f5-5e5d-4c95-9fb3-d42eb1995330)
![Capture d’écran (205)](https://github.com/Grubuntu/PieMenu/assets/56045316/6364fc68-dc68-4f71-9aec-02cef1606133)


- New ToolBars tab: Ability to create a pieMenu from an existing Freecad toolbar in the preferences menu:
  
![Capture d’écran (204)](https://github.com/Grubuntu/PieMenu/assets/56045316/03a3063c-6619-428f-9f4d-64f640c7bb34)

- Experimental feature: long right click open the current PieMenu:
#### (Try it at your own risk: this may cause unexpected behaviour depending on the mouse settings (CAD, Blender, OpenScad etc) 
![Capture d’écran (202)](https://github.com/Grubuntu/PieMenu/assets/56045316/798d5c8d-e09d-499c-b5bb-5645b322b7b3)

### Version 1.7 new features:

- Added Piemenu preview in Preferences : We can now easily adjust the PieMenus settings thanks to the immediate display of the PieMenu in the settings window.


![Capture d’écran (223)](https://github.com/Grubuntu/PieMenu/assets/56045316/70de42e6-e34e-4d51-907d-f53cdf007c98)



- Introduction of context immediate trigger:

When the immediate context trigger mode is ticked and the trigger conditions are obtained (selection of edges, faces, etc.), the PieMenu will be displayed immediately without pressing the keyboard shortcut.
You can set context mode individually for each PieMenu.

![Capture d’écran (222)4](https://github.com/Grubuntu/PieMenu/assets/56045316/c68f0ef7-d944-4013-82ec-a5d254b96cdb)

You can set a single workbench in which the context will be triggered:

![Capture d’écran (222)5](https://github.com/Grubuntu/PieMenu/assets/56045316/4a39fecd-9da8-4050-af1b-a2d45a0f41b6)


(it is still possible to deactivate or activate globaly the context mode with the global parameter).
![Capture d’écran (219)](https://github.com/Grubuntu/PieMenu/assets/56045316/0f82c3cc-3951-497f-ac5f-054ee1f359e2) ![Capture d’écran (216)](https://github.com/Grubuntu/PieMenu/assets/56045316/a7359a26-cabf-44d3-b316-583ff2ddc970)


- New interface for adding existing FreeCAD's toolbars:

![Capture d’écran (221)](https://github.com/Grubuntu/PieMenu/assets/56045316/313185d9-cb42-4656-9abe-3228e7aff3fc)

