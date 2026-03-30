from dataclasses import dataclass, field
@dataclass
class AppState:
    context_all: dict = field(default_factory=dict)

    shortcut_key: str = ""
    global_shortcut_key: str = "TAB"
    hover_delay: int = 100
    flag_shortcut_override: bool = False
    # first_load: bool = True

    # # simple collections
    # shortcut_list: list = field(default_factory=list)
    # list_commands: list = field(default_factory=list)
    # list_shortcut_code: list = field(default_factory=list)

app_state = AppState()

