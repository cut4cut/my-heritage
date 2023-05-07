from dataclasses import field, dataclass


@dataclass
class MediaPhoto:
    file: bytes
    title: str
    period: str
    caption: str = field(init=False)
    period_symbs: set = field(
        default_factory=lambda: set(["-", "–", "—", "‒", "―", "⸺", "⸻"])
    )

    def prep_period(self) -> str:
        if any((symb in self.period_symbs) for symb in self.period):
            return f"Период {self.period}"
        return f"Год {self.period}"

    def __post_init__(self) -> None:
        self.caption = ". ".join([self.title, self.prep_period()])
