# PieMenu
PieMenu widget for FreeCAD 

Quick customizable menus for FreeCAD.


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
PieMenu can be installed via the FreeCAD add-on manager. 

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

### Usage
Press the Tab key on the keyboard to invoke PieMenu or set shortcut via Accessories Menu





### Discussion
FreeCAD forum thread: https://forum.freecad.org/viewtopic.php?t=84101


Thanks to all the work done by mdkus, triplus, looo, microelly.

