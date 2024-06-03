# CHANGELOG

### 1.6

- Added ability to add a custom icon for each PieMenu (SVG or ICO)
- Added ability to call a PieMenu in an other PieMenu (nested PieMenu)
- Added new Toolbars tab in Preferences setting for adding existing FreeCAD's toolbar as new PieMenu
- Added experimental feature : long right click can open the current PieMenu
- Added offset of 1/2 icon for outer rings for Concentric shape

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





  








