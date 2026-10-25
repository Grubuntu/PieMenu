from dataclasses import dataclass, field


@dataclass
class AppState:
    context_all: dict = field(default_factory=dict)

    shortcut_key: str = ""
    global_shortcut_key: str = "TAB"
    hover_delay: int = 100
    flag_shortcut_override: bool = False
    first_load: bool = True

    list_commands: list = field(default_factory=list)
    list_shortcut_code: list = field(default_factory=list)
    row_subgroup_map: dict[int, str] = field(default_factory=dict)
    sub_group_selected: str | None = None

    loaded_workbenches: list = field(default_factory=list)
    signs: dict = field(default_factory=dict)
    sort_order: object = None
    context_phase: bool = False
    compositing_manager: bool = True
    window_shadow: bool = True

    wizard_running: bool = False
    assistant_active: bool = False

    trigger_mode: str = "Press"
    pie_menu_instance: object = None
    action_key: object = None
    pie_menu_dialog: object = None
    sel_observer: object = None


app_state = AppState()
