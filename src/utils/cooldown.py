import time


class Cooldown:
    """
    This class is used to create cooldowns for the agent.

    Attributes:
        per (int): Cooldown period
        _cooldown (dict[str, float]): Dictionary containing the key and the time when the key was last used

    """

    def __init__(self, per: int) -> None:
        self.per = per
        self._cooldown: dict[str, float] = {}

    def on_waiting(self, key: str) -> bool:
        """
        This function is used to check if the key is on cooldown.

        Args:
            key (str): Key to check

        Returns:
            bool: True if key is on cooldown, False otherwise

        """
        current = time.time()  # get current time in seconds since epoch
        if current - self._cooldown.get(key, 0) < self.per:
            return True
        return False

    def update(self, key: str) -> None:
        """
        This function is used to update the cooldown for the key.

        Args:
            key (str): Key to update

        Returns:
            None

        """
        self._cooldown[key] = time.time()
