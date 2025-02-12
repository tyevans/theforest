from rich import print
from rich.table import Table


def print_map(forest):
    table = Table(show_header=False)

    for y in range(forest.height):
        row = []
        for x in range(forest.width):
            tile = forest.get_tile_at(x, y)
            num_actors = len(tile.list_actors())
            if num_actors:
                cell = f"[red]{num_actors}[/red]"
            else:
                cell = f"[bold green]{num_actors}[/bold green]"
            row.append(cell)
        table.add_row(*row)

    print(table)
