from rich.table import Table

def generate_map_table(forest, player_location):
    table = Table(show_header=False)

    for y in range(forest.height):
        row = []
        for x in range(forest.width):
            tile = forest.get_tile_at(x, y)
            num_actors = len(tile.list_actors())
            if player_location is tile:
                cell_color = "bold blue"
            elif num_actors:
                cell_color = "bold red"
            else:
                cell_color = "white"

            cell = f"[{cell_color}]{num_actors}[/{cell_color}]"
            row.append(cell)
        table.add_row(*row)

    return table
