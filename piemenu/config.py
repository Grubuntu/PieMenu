from piemenu import constants

PARAM_PATH       = "User parameter:BaseApp/PieMenu"
PARAM_INDEX_PATH = "User parameter:BaseApp/PieMenu/Index"
PARAM_ACCENTS    = "User parameter:BaseApp/Preferences/Themes"
PARAM_COLOR      = "User parameter:BaseApp/Preferences/View"

def get_params():
    """Return the FreeCAD parameter groups used by PieMenu (main, index, accents, color)."""
    import FreeCAD as App
    return {
        "main":    App.ParamGet(PARAM_PATH),
        "index":   App.ParamGet(PARAM_INDEX_PATH),
        "accents": App.ParamGet(PARAM_ACCENTS),
        "color":   App.ParamGet(PARAM_COLOR),
    }


def get_loaded_workbenches():
    import FreeCAD as App
    paramLoadedWb = "User parameter:BaseApp/Preferences/General"
    paramWb = App.ParamGet(paramLoadedWb)
    return paramWb.GetString("BackgroundAutoloadModules").split(",")


def get_param_index(name):
    """Get parameter from User parameter:BaseApp/PieMenu/Index."""
    value = get_params()["index"].GetString(name)
    return value


def get_param(name):
    """Get parameter from User parameter:BaseApp/PieMenu."""
    value = get_params()["main"].GetString(name)
    return value


def get_parameter_global(paramType="String", paramName=""):
    """Get parameter from user parameters."""
    if paramType == "String":
        parameter = get_params()["main"].GetString(paramName)
    elif paramType == "Int":
        parameter = get_params()["main"].GetInt(paramName)
    elif paramType == "Bool":
        parameter = get_params()["main"].GetBool(paramName)
    else:
        pass
    return parameter


def get_index_list():
    """Get current pieMenus using available index."""
    indexList = get_params()["index"].GetString(constants.PARAM_INDEX_LIST)
    if indexList:
        indexList = list(map(int, indexList.split(".,.")))
    else:
        indexList = []
    return indexList


def get_parameter_group(keyValue=None, paramType="String", paramName=""):
    """Get parameter in settings, paramType = "String", "Int", "Bool"."""
    parameter = ""

    if keyValue is None:
        keyValue = get_param(constants.PARAM_CURRENT_PIE)
    indexList = get_index_list()
    for i in indexList:
        pieName = get_param_index(str(i))
        if pieName == keyValue:
            param = get_params()["index"].GetGroup(str(i))
            if paramType == "String":
                parameter = param.GetString(paramName)
            elif paramType == "Int":
                parameter = param.GetInt(paramName)
            elif paramType == "Bool":
                parameter = param.GetBool(paramName)
            else:
                pass
    return parameter


def set_parameter_group(keyValue=None, paramType="String", paramName="", paramValue=None):
    """Set parameter in settings, paramType = "String", "Int", "Bool"."""
    indexList = get_index_list()
    for i in indexList:
        pieName = get_param_index(str(i))
        if pieName == keyValue:
            param = get_params()["index"].GetGroup(str(i))
            if paramType == "String":
                param.SetString(paramName, paramValue)
            elif paramType == "Int":
                param.SetInt(paramName, paramValue)
            elif paramType == "Bool":
                param.SetBool(paramName, paramValue)
            else:
                pass
