# CHANGELOG
### 1.9.4
Fix [#106] : FreeCAD crash when we quit Sketcher with PieMenu validation button and 'Sketcher_Dimension'/'Sketcher_CompDimensionTools' is active
Added ability to move or delete severals command at the same time in list tools : [#105](https://github.com/Grubuntu/PieMenu/issues/105)

### 1.9.3
- Fix copy PieMenu not duplicate all parameters https://github.com/Grubuntu/PieMenu/issues/104
- Partially fix (https://github.com/Grubuntu/PieMenu/issues/106)

### 1.9.2
- Qt6 fix : pressing the global shortcut no longer opens PieMenu
- Qt6 fix : modifiers shortcut were broken
- Qt6 fix : keyValue == False in updateCommands()
 -Qt6 fix : function onToolListWidget() were broken, setting showquickmenu were broken
- Qt6 fix : workbenches toolbars were broken
- Qt6 fix : context mode and setting globalcontext were instable
- Qt6 fix : add eventfilter to catch "minimize event", remove WA_MacAlwaysShowToolWindow : not supported in the same way in Qt5
- Fix : setting immediate trigger
- Fix :problem in createpie (add onpiechange()) to update values after create a new PieMenu

### 1.9.1
- Fix window_icon that appears under the dialog window on Linux system

### 1.9
- Added the ability to use FreeCAD's built-in icons for PieMenus (https://github.com/Grubuntu/PieMenu/issues/97)

### 1.8.1
- Use join() method from path module (as WIP-UIFile)
- Fix issue : https://github.com/Grubuntu/PieMenu/issues/94
- Fix some useless code

### 1.8
- Added import/export PieMenu settings
- Clean some code
  
### 1.7.6
- Fix issue : PieMenu crash at launch with Freecad 0.22 Version above 38001 (https://github.com/Grubuntu/PieMenu/issues/89)
  
### 1.7.5
- Fix issue : when left click in PiemenuDialog, it hid the preview

### 1.7.4
- Fix error message on hover in preview toolbartab
- Fix flickering when multi selections (CTRL) on context mode
- Fix submenus in sketcher edit mode : https://github.com/Grubuntu/PieMenu/issues/87

### 1.7.3
Fix issue with the preselection buttons on hover

### 1.7.2
Fix issue with the  display of the preselection button

### 1.7.1
Fix issue https://github.com/Grubuntu/PieMenu/issues/83 and some warnings about 'font size < 0'

### 1.7

- Added Piemenu preview in Preferences
- Move cBox to the up of settings, disable it when toolBarTab is active
- Fix cBox order
- Added Preselect arrow feature
- Added ability to set a WB for Context mode
- Added added management of the CTRL key for multiple selection in Context mode
- Remove button size limitation and set mini and maxi button size (16-120)
- Remove PiemenuDialog fixed size, position and set it modal.
- Fix cBox index to CurrentPie when the Preferences settings are opened
- Fix icon definition for default PieMenu
- Introduction of context immediate trigger with setting in contextTab

### 1.6

- Added ability to add a custom icon for each PieMenu (SVG or ICO)
- Added ability to call a PieMenu in an other PieMenu (nested PieMenu)
- Added new Toolbars tab in Preferences setting for adding existing FreeCAD's toolbar as new PieMenu
- Added experimental feature : long right click can open the current PieMenu
- Added offset of 1/2 icon for outer rings for Concentric shape
- Fix pyside inconsistent imports

### 1.5.1
- Fix problem : the workbenches were no longer available in the PieMenus due to FreeCAD 0.22Dev code changes
  
### 1.5
- Added expressions in fast spinbox
- Added DEL, SUPPR, UP and DOWN key for delete and move Tools il toollist (Settins > Tools tab)
- Added documentation link to wiki
- Added Icon PieMenu to Preference dialog window
- Added toogle behavior for individuals shortcuts (Limitation : works only for -ONE KEY- shortcuts or -'Modifier' + KEY- shortcuts (not for multikeysequence shortcuts eg. -V,G-)
- Added tools shortcuts keys ('0 to 9' and 'A to Z', except 'X' which bug), update stylesheet according to this new feature
- Enable the tools shortcuts will add a column with shortcuts in toollist
- Added show/hide tools's shortcuts : + spinbox for selected font size
- Added buttons to clear shortcut and globalshortcut
- Added checkbox to set the defaut PieMenu in Preferences
- Highlighting the default PieMenubox by an arrow in front in PieMenu's list and in QuickMenu
- Added validation with 'Enter' and 'Return' keys, when buttons "Validate" and "Cancel" are visible.(as a side-effect, pressing the Enter and return keys also hides the PieMenu)
- Matches the style of the Preferences window with the style of FreeCAD Preferences: Groupboxes, Checkboxes left aligned, Spinbox stretched etc
- Rearranging code

### 1.4.2
- Fix problem: when adding WB that doesn't exist in other FreeCAD version, example: AssemblyWB exists in 0.22 but not in 0.21.
  
### 1.4.1
- Fix bug with workbench associated

### 1.4
- Added workbench associated setting
- Added triggermode setting for each PieMenu
- Added global shortcut toggle mode setting
- Clean some code
- Fix vertical alignment for labels in Preferences
- Added ability to add separators in PieMenu
- Added save settings to disk when you close the preferences window
- Update script for update translation
- Added Polish translation

### 1.3.9
- Fix spacing with command names for Pie shape
- Fix style for command name LeftRight shape
- Added shapes:"Concentric" and "Star"
- Added ability to open PieMenu without file opened

### 1.3.8.2
- Added support for theme accent color (FreeCad>Preferences>Display>Theme>Accent Color)
- Fix default stylesheet to Legacy.qss if no existing stylesheet is set
- Added stylesheet Accents.qss

### 1.3.8.1
- Fix issue with stylesheet

### 1.3.8
- Added a checkbox in fast spinbox mode for Pocket/Pad : Through all, Symmetric, Reversed
- Changing spinbox type to accept calculations and added units
- Reactivation of the quickmenu in the sketcher, the problem seems resolved (def getGroup())
- Fix some bugs : problem when create a ToolBar via QuickMenu, problem with command name setting...
- Remove some useless/duplicate code (def actualizeWorkbenchActions)  
- Rearrangement of menu priorities for Global shortcut: Sketcher, Context, ToolBar, Current Pie (def updateCommands)
- Added command name for LeftRight shape (Pgilfernandez)
- Added French Support

### 1.3.7
- Add translation support, Spanish translation, Small cleanup.(hasecilu) 
- Add Icon spacing, stylabe QuickMenu and many cosmetics improvements (Pgilfernandez)
- Add new shape Left and Right (Pgilfernandez)
- Fix random bug with eventfilter

### 1.3.6
- Update layout of PieMenu Preferences for better readability (Pgilfernandez)
- Fix some typos (Pgilfernandez)
- Added some styles for QLabel command name (Pgilfernandez)
- Added "LeftRight" shape
- Fix problem with ghosting when reload workbenches

### 1.3.5
- Factorization and clean some code
- Added differents shapes for PieMenus
- Added possibility to display the command name in the menu (only Pie shape)
- Added a button with information about developers and licence (Pgilfernandez)
  
### 1.3.4
- Move globals settings on a new tab
- Added setting for show or not the QuickMenu
- Added checkbox in parameters for Contextual activation
- Set default theme (Legacy) on a new installation
- Update stylesheets for #styleButtonMenu::menu-indicator (setting for QuickMenu)





  








