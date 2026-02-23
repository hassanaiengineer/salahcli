from rich.table import Table

def prayer_table() -> Table:
    table = Table(show_header=False, expand=True, padding=(0, 2), box=None)
    table.add_column("Prayer", justify="left")
    table.add_column("Time", justify="right")
    return table
