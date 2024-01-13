# PieMenu Improved
PieMenu widget for FreeCAD 

![Capture d’écran (8)](https://github.com/Grubuntu/PieMenu-Improved/assets/56045316/95ce9087-06d2-4b5f-bffc-6bf867afadb6)


### Installation
PieMenu (1.2.7) can be installed via the FreeCAD add-on manager
You should replace originals files by this version in directory Mod/PieMenu.

Or just add all files in a PieMenu directory in your FreeCAD Mod directory.
![Capture d’écran (21)](https://github.com/Grubuntu/PieMenu-Improved/assets/56045316/a0fbcb3e-a5c5-4687-93ed-5b734e1ef63a)

(Windows) Or in  %AppData%\FreeCAD\Mod\

![Capture d’écran (20)](https://github.com/Grubuntu/PieMenu-Improved/assets/56045316/2acee710-2cee-42f3-ab3a-4e10c94d27af)

Install path for FreeCAD modules depends on the operating system used.

##### Examples:

Linux:

`/home/user/.FreeCAD/Mod/PieMenu/InitGui.py`

macOS:

`/Users/user_name/Library/Preferences/FreeCAD/Mod/PieMenu/InitGui.py`

Windows:

`C:\Users\user_name\AppData\Roaming\FreeCAD\Mod\PieMenu\InitGui.py`

### Usage
Press the Tab key on the keyboard to invoke PieMenu or set shortcut via Accessories Menu

Validate or Cancel, change length/size value directly with spinbox during editing of a function (Pad, Pocket, Chamfer, Fillet, Thickness)

![Capture d’écran (1)](https://github.com/Grubuntu/PieMenu-Improved/assets/56045316/9ac46209-a050-4571-b9bf-0832c93315ba)


'Sketcher' PieMenu is a special PieShortcutBar, which is called when you edit a sketch in Sketcher.

![Capture d’écran (2)](https://github.com/Grubuntu/PieMenu-Improved/assets/56045316/1a449eda-b29a-40de-b06d-b55f672a4aa2)



Choose between 2 themes (Transparent, Legacy)

![Capture d’écran (10)](https://github.com/Grubuntu/PieMenu-Improved/assets/56045316/30f21f77-24ad-4491-bc75-11538d2ab527)
![Capture d’écran (19)](https://github.com/Grubuntu/PieMenu-Improved/assets/56045316/5339d57d-785b-4e27-a410-c79677c3d8b1)


Can change the global shortcut and can assign a shortcut for each PieMenu, remove shortcuts by assigning an empty shortcut.

![Capture d’écran (9)](https://github.com/Grubuntu/PieMenu-Improved/assets/56045316/c3f60d95-d675-4d6a-a740-a0dbcf678a67)



### Discussion
FreeCAD forum thread: https://forum.freecad.org/viewtopic.php?t=84101



Thanks to all the work done by mdkus, triplus, looo, microelly.

# PieMenu widget for FreeCAD

# Copyright (C) 2024 Grubuntu @ FreeCAD
# Copyright (C) 2022, 2023 mdkus @ FreeCAD
# Copyright (C) 2016, 2017 triplus @ FreeCAD
# Copyright (C) 2015,2016 looo @ FreeCAD
# Copyright (C) 2015 microelly <microelly2@freecadbuch.de>
#
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

# Attribution:
# http://forum.freecadweb.org/
# http://www.freecadweb.org/wiki/index.php?title=Code_snippets

# Changelog :
# 1.2.8 : 
# Added validation/cancel buttons for validate or close features window rapidly
# Added interactive spinbox for editing length/angle/size in features Pad, Pocket, Chamfer, Fillet, Thickness, Revolution
# Added transparent theme : choose via settings menu
# Added Sketcher context menu : show in context SketcherWB
# Added tempo on the hover to avoid too fast triggering
# Added 'PartDesign' and 'Sketcher' menu at first launch 
# Removed close button (useless, we can click outside the widget to close it)
#
# 1.2.9 : 
# Added ability to set global keyboard shortcut in settings menu
#
# 1.2.9.1 : 
# Correction for Theme setting
#
# 1.3.0 : 
# Added ability to set a keyboard shortcut for each PieMenu
