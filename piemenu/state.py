from dataclasses import dataclass, field
@dataclass
class AppState:
    context_all: dict = field(default_factory=dict)

app_state = AppState()
