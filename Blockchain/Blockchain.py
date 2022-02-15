class Blockchain():
    def __init__(self, blocks=[]) -> None:
        self.blocks = blocks

    def __str__(self) -> str:
        output = ""
        for block in self.blocks:
            output += f"#{block.index} with hash {block.hash} {f'with previous hash {block.prev_hash}' if block.prev_hash else ''}\n"
        return output
