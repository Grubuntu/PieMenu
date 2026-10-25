from piemenu import resources, state


class PieMenuSeparator():
    """Class PieMenuSeparator"""

    def __init__(self):
        pass

    def GetResources(self):
        """Return a dictionary with data that will be used by the button or menu item."""
        import FreeCAD as App
        translate = App.Qt.translate
        return {'Pixmap': resources.iconAddSeparator,
                'MenuText': translate('PieMenuTab', 'Separator'),
                'ToolTip': translate('PieMenuTab', 'Separator for PieMenu ')}

    def Activated(self):
        """Run the following code when the command is activated (button press)."""
        pass

    def IsActive(self):
        """Return True when the command should be active or False when it should be disabled (greyed)."""
        return False


class NestedPieMenu():
    """Class nested PieMenu """

    def __init__(self, keyValue, iconPath=None):
        self.iconPath = resources.iconPieMenuLogo
        self.keyValue = keyValue

    def GetResources(self):
        """Return a dictionary with data that will be used by the button or menu item."""
        return {'Pixmap': self.iconPath,
                'MenuText': self.keyValue,
                'ToolTip': self.keyValue,
                'CmdType': 'ForEdit'}

    def Activated(self):
        """Run the following code when the command is activated (button press)."""
        instance = state.app_state.pie_menu_instance
        if instance:
            instance.showAtMouseInstance(self.keyValue)

    def IsActive(self):
        """Return True when the command should be active or False when it should be disabled (greyed)."""
        return True

    def setIconPath(self, icon_path):
        """Set the icon path for the NestedPieMenu instance."""
        self.iconPath = icon_path
