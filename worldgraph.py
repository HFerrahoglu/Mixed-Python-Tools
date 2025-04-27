import osmnx as ox
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, BarColumn, TimeElapsedColumn
import os

console = Console()

LENGTH_STYLES = [
    (100, 0.10, "#a6a6a6"),
    (200, 0.15, "#676767"),
    (400, 0.25, "#454545"),
    (800, 0.35, "#d5d5d5"),
    (float("inf"), 0.45, "#ededed"),
]

NETWORK_OPTIONS = {
    "1": ("Tüm yollar (Önerilen)", "all"),
    "2": ("Sadece araç yolları", "drive"),
    "3": ("Yaya yolları", "walk"),
    "4": ("Bisiklet yolları", "bike"),
}

ASCII_ART = """
[bold cyan]
     __    __           _     _   ___                 _     
    / / /\ \ \___  _ __| | __| | / _ \_ __ __ _ _ __ | |__  
    \ \/  \/ / _ \| '__| |/ _` |/ /_\/ '__/ _` | '_ \| '_ \ 
     \  /\  / (_) | |  | | (_| / /_\\| | | (_| | |_) | | | |
      \/  \/ \___/|_|  |_|\__,_\____/|_|  \__,_| .__/|_| |_|
                                               |_|          
[/bold cyan]
"""

def get_road_style(length: float):
    for max_length, linewidth, color in LENGTH_STYLES:
        if length <= max_length:
            return linewidth, color
    return 0.10, "#a6a6a6"

def ensure_output_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)

def create_artistic_map(
    province_name: str,
    country_name: str,
    background_color: str,
    output_dir: str,
    dpi: int,
    network_type: str,
):
    location = f"{province_name}, {country_name}"
    ensure_output_dir(output_dir)

    print(f"[bold cyan]Harita verileri indiriliyor: [/] [green]{location}[/] ([yellow]{network_type} ağı[/])")

    with Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        BarColumn(),
        TimeElapsedColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Veri çekiliyor...", total=None)
        try:
            graph = ox.graph_from_place(
                location,
                retain_all=True,
                simplify=True,
                network_type=network_type
            )
            progress.update(task, completed=100)
        except Exception as e:
            print(f"[bold red]Veri çekme hatası:[/] {e}")
            return

    print("[bold cyan]Yollar işleniyor...[/]")
    edge_data = list(graph.edges(keys=True, data=True))
    road_colors = []
    road_widths = []

    for _, _, _, data in edge_data:
        linewidth, color = get_road_style(data.get("length", 0))
        road_colors.append(color)
        road_widths.append(float(linewidth))

    print("[bold cyan]Harita çiziliyor...[/]")
    fig, ax = ox.plot_graph(
        graph,
        node_size=0,
        figsize=(27, 40),
        dpi=dpi,
        bgcolor=background_color,
        save=False,
        edge_color=road_colors,
        edge_linewidth=road_widths,
        edge_alpha=1,
        show=False
    )

    fig.tight_layout(pad=0)

    filename = f"{province_name}_{country_name}_map.png".replace(' ', '_')
    output_path = os.path.join(output_dir, filename)

    fig.savefig(
        output_path,
        dpi=dpi,
        bbox_inches="tight",
        format="png",
        facecolor=fig.get_facecolor(),
        transparent=False
    )

    print(f"\n[bold green]Harita başarıyla kaydedildi[/] [yellow]{output_path}[/]")

def show_menu():
    console.clear()
    print(ASCII_ART)
    print("[bold magenta]WorldGraph[/]")

    province = Prompt.ask("\n[bold blue]Şehir adını girin (örn: Paris)[/]").strip()
    if not province:
        print("[bold red]Geçerli bir şehir adı girmelisin![/]")
        return

    country = Prompt.ask("\n[bold blue]Ülke adını girin (örn: France)[/]").strip()
    if not country:
        print("[bold yellow]Ülke belirtilmedi. 'Turkey' olarak varsayılacak.[/]")
        country = "Turkey"

    print("\n[bold blue]Ağ tipi seçin:[/]")
    for key, (desc, _) in NETWORK_OPTIONS.items():
        print(f"[cyan]{key}.[/] {desc}")

    network_choice = Prompt.ask("\n[bold blue]Seçiminizi yapın (örn: 1)[/]", choices=list(NETWORK_OPTIONS.keys()), default="1")
    network_type = NETWORK_OPTIONS[network_choice][1]

    dpi = Prompt.ask("\n[bold blue]Çözünürlük (DPI) değeri girin (varsayılan 600)[/]", default="600")
    try:
        dpi = int(dpi)
    except ValueError:
        dpi = 600

    bgcolor = Prompt.ask("\n[bold blue]Arkaplan rengi girin (hex kodu, varsayılan #061529)[/]", default="#061529")
    output_dir = Prompt.ask("\n[bold blue]Çıktı dosya dizini (varsayılan ./haritalar)[/]", default="./haritalar")

    create_artistic_map(
        province_name=province,
        country_name=country,
        background_color=bgcolor,
        output_dir=output_dir,
        dpi=dpi,
        network_type=network_type,
    )

if __name__ == "__main__":
    show_menu()
