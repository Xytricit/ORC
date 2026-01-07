"""CLI progress helpers (skeleton)."""
import time


class Progress:
    def __init__(self, total: int = 0):
        self.total = total
        self.current = 0

    def advance(self, n: int = 1):
        self.current += n

    def done(self):
        self.current = self.total
