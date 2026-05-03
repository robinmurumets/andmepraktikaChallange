"""Tee arvutatud tõenäosustest lihtne x-telje skaala."""

import matplotlib.pyplot as plt


def vorminda_tõenäosus(tõenäosus):
    """Vormindab tõenäosuse protsendi ja komakohana."""
    return f"{tõenäosus:.1%} ({tõenäosus:.3f})"


def loo_graafik(tõenäosused, pildi_fail):
    """Loob lineaarse 0-1 tõenäosuste skaala ja salvestab pildi."""
    pildi_fail.parent.mkdir(exist_ok=True)

    joonis, telg = plt.subplots(figsize=(13, 4.2))
    värvid = tõenäosused["allikas"].map(
        {"Statistikaamet": "#5B2A86", "Võrdluspunkt": "#1B998B"}
    )
    y_kohad = [0] * len(tõenäosused)

    telg.scatter(tõenäosused["tõenäosus"], y_kohad, s=105, c=värvid, zorder=3)
    telg.axhline(0, color="#2D3142", linewidth=1.6)

    for järjekord, rida in enumerate(tõenäosused.itertuples()):
        tekst = f"{rida.sündmus}\n{vorminda_tõenäosus(rida.tõenäosus)}"
        nihke_suund = 1 if järjekord % 2 == 0 else -1
        telg.annotate(
            tekst,
            xy=(rida.tõenäosus, 0),
            xytext=(0, 38 * nihke_suund),
            textcoords="offset points",
            ha="center",
            va="bottom" if nihke_suund > 0 else "top",
            fontsize=9,
            arrowprops={"arrowstyle": "-", "color": "#4F5D75", "linewidth": 0.8},
        )

    telg.set_xlim(0, 1)
    telg.set_ylim(-0.55, 0.55)
    telg.set_yticks([])
    telg.set_xlabel("Tõenäosus / osakaal")
    telg.set_title("Tõenäosuste skaala")
    telg.grid(axis="x", linestyle="--", linewidth=0.6, alpha=0.35)
    telg.set_facecolor("#FAF7F0")
    joonis.patch.set_facecolor("#FAF7F0")

    for külg in ["left", "right", "top"]:
        telg.spines[külg].set_visible(False)

    legendikirjed = [
        plt.Line2D([], [], marker="o", linestyle="", color="#5B2A86", label="Statistikaamet"),
        plt.Line2D([], [], marker="o", linestyle="", color="#1B998B", label="Võrdluspunkt"),
    ]
    telg.legend(handles=legendikirjed, loc="lower right")

    joonis.tight_layout()
    joonis.savefig(pildi_fail, dpi=180)
    plt.close(joonis)
