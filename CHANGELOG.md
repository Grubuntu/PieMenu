# CHANGELOG

### 1.3.4

- Move globals settings on a new tab
- Added setting for show or not the QuickMenu
- Added checkbox in parameters for Contextual activation
- Set default theme (Legacy) on a new installation
- Update stylesheets for #styleButtonMenu::menu-indicator (setting for QuickMenu)

### 1.3.5

- Factorization and clean some code
- Added differents shapes for PieMenus
- Added possibility to display the command name in the menu (only Pie shape)
- Added a button with information about developers and licence (Pgilfernandez)

### 1.3.6

- Update layout of PieMenu Preferences for better readability (Pgilfernandez)
- Fix some typos (Pgilfernandez)
- Added some styles for QLabel command name (Pgilfernandez)
- Added "LeftRight" shape
- Fix problem with ghosting when reload workbenches

### 1.3.7

- Add translation support, Spanish translation, Small cleanup.(hasecilu) 
- Add Icon spacing, stylabe QuickMenu and many cosmetics improvements (Pgilfernandez)
- Add new shapes Left and Right (Pgilfernandez)
- Fix random bug with eventfilter
  
### 1.3.8       
Added a checkbox for Pocket : Through all, Symmetric, Reversed
Changing spinbox type to accept calculations
Added units in spinbox
Reactivation of the quickmenu in the sketcher, the problem seems resolved (def getGroup())
Fix bug when create ToolBar via QucikMenu : options from the preferences window could be displayed (def onPieChange())  
Remove some useless/duplicate code (def actualizeWorkbenchActions)  
Rearrangement of menu priorities for Global shortcut: Sketcher, Context, ToolBar, Current Pie (def updateCommands)
