
def get_signs():

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

listSpinboxFeatures = ['<PartDesign::Fillet>', '<PartDesign::Chamfer>', '<PartDesign::Thickness>',
                       '<PartDesign::Pad>', '<PartDesign::Pocket>', '<PartDesign::Revolution>']

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
