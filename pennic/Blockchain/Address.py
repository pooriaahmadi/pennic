class Address():
    def __init__(self, ip: int, port: int = None) -> None:
        self.ip = ip
        self.port = port or 34756

    def __str__(self) -> str:
        return f"{self.ip}:{self.port}"
