
def get_signs():
    """Return a mapping of comparison sign strings to operator functions."""
    import operator

    return {
        "<": operator.lt,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne,
        ">": operator.gt,
        ">=": operator.ge,
    }
touches_speciales = {'CTRL', 'ALT', 'SHIFT', 'META', 'TAB'}
available_shape = ["Pie", "RainbowUp", "RainbowDown", "Concentric", "Star", "UpDown", "LeftRight",
                   "TableTop", "TableDown", "TableLeft", "TableRight"]

# Parameter names stored in the FreeCAD user configuration.
# Using these constants instead of raw strings prevents typos and makes
# refactoring safe (the "EnableShorcut" typo is preserved for backward compat).
PARAM_CURRENT_PIE = "CurrentPie"
PARAM_CONTEXT_PIE = "ContextPie"
PARAM_INDEX_LIST = "IndexList"
PARAM_TOOL_LIST = "ToolList"
PARAM_TOOL_BAR = "ToolBar"
PARAM_ICON_PATH = "IconPath"
PARAM_THEME = "Theme"
PARAM_GLOBAL_SHORTCUT_KEY = "GlobalShortcutKey"
PARAM_GLOBAL_KEY_TOGGLE = "GlobalKeyToggle"
PARAM_SHOW_QUICK_MENU = "ShowQuickMenu"
PARAM_DISPLAY_SPIN_BOX = "DisplaySpinBox"
PARAM_ENABLE_CONTEXT = "EnableContext"
PARAM_DELAY_RIGHT_CLICK = "DelayRightClick"
PARAM_RIGHT_CLICK_TRIGGER = "RightClickTrigger"
PARAM_RADIUS = "Radius"
PARAM_BUTTON = "Button"
PARAM_NUM_COLUMN = "NumColumn"
PARAM_ICON_SPACING = "IconSpacing"
PARAM_COMMAND_PER_CIRCLE = "CommandPerCircle"
PARAM_SHORTCUT_LABEL_SIZE = "ShortcutLabelSize"
PARAM_HOVER_DELAY = "HoverDelay"
PARAM_TRIGGER_MODE = "TriggerMode"
PARAM_SHAPE = "Shape"
PARAM_DISPLAY_COMMAND = "DisplayCommand"
PARAM_DISPLAY_PRESELECT = "DisplayPreselect"
PARAM_DISPLAY_SHORTCUT = "DisplayShorcut"
PARAM_ENABLE_SHORTCUT = "EnableShorcut"  # NOTE: typo preserved for backward compat
PARAM_SHORTCUT_KEY = "ShortcutKey"
PARAM_DEFAULT_WORKBENCH = "DefaultWorkbench"
PARAM_CONTEXT_WORKBENCH = "ContextWorkbench"


import math


def compute_shape_angle(shape, commandNumber, command_per_circle):
    """Return (angle, angleStart) for the given shape.

    Pure helper extracted from ``PieMenu.add_commands`` so it can be unit-tested
    without a running FreeCAD GUI.
    """
    if shape == "Pie":
        if commandNumber == 1:
            angle = 0
        else:
            angle = 2 * math.pi / commandNumber
        angleStart = 3 * math.pi / 2 - angle
    elif shape == "RainbowUp":
        if commandNumber == 1:
            angle = 0
        else:
            angle = math.pi / (commandNumber - 1)
        angleStart = 3 * math.pi / 2 - (angle * (commandNumber + 1)) / 2
    elif shape == "RainbowDown":
        if commandNumber == 1:
            angle = 0
        else:
            angle = math.pi / (commandNumber - 1)
        angleStart = math.pi / 2 - (angle * (commandNumber + 1)) / 2
    elif shape == "Concentric" or shape == "Star":
        angle = 2 * math.pi / (command_per_circle)
        angleStart = 3 * math.pi / 2 - angle
    else:
        angle = 2 * math.pi / commandNumber
        angleStart = 3 * math.pi / 2 - angle
    return angle, angleStart

listSpinboxFeatures = ['<PartDesign::Fillet>', '<PartDesign::Chamfer>', '<PartDesign::Thickness>',
                       '<PartDesign::Pad>', '<PartDesign::Pocket>', '<PartDesign::Revolution>']

# Mapping from a PartDesign feature type to the property written by the fast
# spinbox. Features not present here (e.g. Hole) hide the spinbox instead.
SPINBOX_SIZE_ATTR = {
    '<PartDesign::Fillet>': 'Radius',
    '<PartDesign::Chamfer>': 'Size',
    '<PartDesign::Thickness>': 'Value',
    '<PartDesign::Pad>': 'Length',
    '<PartDesign::Pocket>': 'Length',
    '<PartDesign::Revolution>': 'Angle',
    '<PartDesign::Groove>': 'Angle',
}

# Features whose fast spinbox uses the MidPlane / Reversed checkboxes.
SPINBOX_MIDPLANE_FEATURES = {
    '<PartDesign::Pad>',
    '<PartDesign::Pocket>',
    '<PartDesign::Revolution>',
    '<PartDesign::Groove>',
}

workbench_map = {
    "Arch": "BIMWorkbench",
    "FEM": "FemWorkbench",
    "SheetMetal": "SMWorkbench",
    "Asm4": "Assembly4Workbench",
    "a2p": "A2plusWorkbench",
    "Materials": "MaterialWorkbench",
    "FCGear": "GearWorkbench",
    "FreeCAD": "Std"
}

defaultTools = ["Std_ViewTop",
                "Std_New",
                "Std_ViewRight",
                "Std_BoxSelection",
                "Std_ViewBottom",
                "Std_ViewIsometric",
                "Std_ViewLeft",
                "Std_ViewScreenShot"]

defaultToolsPartDesign = ["PartDesign_NewSketch",
                          "PartDesign_Pad",
                          "PartDesign_Pocket",
                          "PartDesign_Chamfer",
                          "PartDesign_Fillet"]

defaultToolsSketcher = ["Sketcher_CreatePolyline",
                        "Sketcher_CompCreateCircle",
                        "Sketcher_CreateRectangle",
                        "Sketcher_ToggleConstruction"]
