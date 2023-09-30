import time


class Cooldown:
    def __init__(self, per: int) -> None:
        self.per = per
        self._cooldown: dict[str, float] = {}

    def on_waiting(self, key: str) -> bool:
        current = time.time()
        if current - self._cooldown.get(key, 0) < self.per:
            return True
        return False

    def update(self, key: str) -> None:
        self._cooldown[key] = time.time()
