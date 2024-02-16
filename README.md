# PieMenu
PieMenu widget for FreeCAD 

Quick customizable menus for FreeCAD.

Presentation: PieMenu is a customizable menu, providing quick access to FreeCAD tools via keyboard shortcuts. You can choose from multiple shapes, themes, customize tools and shortcuts, and much more... 

Warning: PieMenu is in development, bugs may still exist. It is necessary to backup your configuration files before any PieMenu installation or update to be able to restore them in case of issues. 

New ! The fast spinbox menu now includes units and some capabilities for making calculations.
Directly modify the length/size/angle value using the spinbox during the editing of Pad, Pocket, Chamfer, Fillet, Thickness, Groove, or Revolution.

![Capture d’écran (98)](https://github.com/Grubuntu/PieMenu/assets/56045316/9a24e5bb-e619-4ed3-b3ce-4977c91cedf3)

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
Select size, shape, tools, individual shortcut for each PieMenu and/or a global shortcut to open a default PieMenu (remove shortcuts by assigning an empty shortcut).

![Capture d’écran (101)](https://github.com/Grubuntu/PieMenu/assets/56045316/bb576592-817d-4f20-aaae-230be850be35)


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

![image](https://github.com/Grubuntu/PieMenu/assets/56045316/a2edd432-33c8-419f-b309-ee8bbb33f7aa)

The QuickMenu allows for quickly adjusting certain settings. If the QuickMenu is not visible, it must be enabled in the "Preferences" by activating the "Show QuickMenu" option.

![image](https://github.com/Grubuntu/PieMenu/assets/56045316/3b73a649-2369-45c2-b1bd-e80c4fedc054)

### 1) PieMenu Tab:

Create a new PieMenu by clicking on the '+' button, name it, and validate. It will now be visible in the dropdown list of PieMenus.
Modify and adjust available settings (settings may vary depending on the PieMenu configuration):

    
    • Menu size: adjusts the size of the menu
    
    • Button size: adjusts the size of the buttons (Note: maximum size depends on the menu size)
    
    • Shape: multiple shapes are available
    
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

![image](https://github.com/Grubuntu/PieMenu/assets/56045316/c5c1c77d-d4de-4369-a6ec-9ed45cfc1371)
![image](https://github.com/Grubuntu/PieMenu/assets/56045316/81ea27c4-a3a2-4c2c-9327-431c1d9c67d5)


### 4) Global settings tab :

Here, you can:

    • Select the theme style
    
    • Enable or disable the QuickMenu (context menu)
    
    • Choose the activation mode: 'On press' or 'On hover' of the mouse.
    
    • Set the hover activation delay: to avoid triggering too quickly when passing over multiple commands, it is necessary to set a sufficient delay.
    
    • Enable or disable the Context mode (also available in the QuickMenu).
    
    • Assign the global shortcut.

![Capture d’écran (114)](https://github.com/Grubuntu/PieMenu/assets/56045316/0a8f21b7-74c9-4923-b008-9ec6a739e65b)

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

![image](https://github.com/Grubuntu/PieMenu/assets/56045316/a8a25206-b775-42cc-90a6-f50e8977e48c)

Click on "PieMenu" to expand the menu and select the desired PieMenu: this will now be activated by default by the global shortcut (a checkmark is visible in front of the default PieMenu, if no checkmark is visible, it means that a ToolBar is currently active by default.


3) Individual Shortcut:

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

3 - Default PieMenu


If the "Context" mode is active and the selection conditions are met, then the PieMenu corresponding to the "Context" will be displayed. 

Otherwise, if a ToolBar is active (via the QuickMenu), then that ToolBar is displayed. 

Otherwise, the default PieMenu (checked in the QuickMenu) will be displayed.

## 5 - Quick Menu Spinbox:

The quick menu spinbox is displayed when pressing the global shortcut during the editing of certain features in the PartDesign workbench: Pad, Pocket, Chamfer, Fillet, Revolution, Groove.

![image](https://github.com/Grubuntu/PieMenu/assets/56045316/742581eb-5884-4a31-a8c4-88945bb2fca3)

It allows quick access to modifying the main value of the function (Length, Depth, Angle, Size, etc.) as well as quick access to certain parameters of the Pad and Pocket functions: 'Through all', 'Symmetric to plane', and 'Reversed'.
It is possible to perform certain calculations in the input box and quickly validate either by pressing the 'Enter' or 'Return' key, or by clicking the 'Validation' button.
