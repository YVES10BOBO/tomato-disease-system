"""
Generates Figure 4.2: Development and Production Deployment Architectures
for the TomatoGuard thesis. Saves figure_4_2_deployment.png.

Run:  python figure_4_2_deployment.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ─── colours ────────────────────────────────────────────────
CLIENT = "#D6EAF8"   # light blue  — devices/clients
TUNNEL = "#FCF3CF"   # light yellow — ngrok tunnel
SERVER = "#D5F5E3"   # light green — backend server
DB     = "#FADBD8"   # light red   — database


def box(ax, x, y, text, color, w=2.6, h=1.1):
    ax.text(
        x, y, text, ha="center", va="center", fontsize=9, zorder=3,
        bbox=dict(boxstyle="round,pad=0.45", facecolor=color,
                  edgecolor="#34495E", linewidth=1.3),
    )


def arrow(ax, x1, y1, x2, y2, label=None, two_way=False):
    style = "<->" if two_way else "->"
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle=style, lw=1.6, color="#34495E",
                        shrinkA=32, shrinkB=32),
        zorder=1,
    )
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.28, label,
                ha="center", va="center", fontsize=7.5, color="#7B241C",
                style="italic", zorder=2)


def draw_panel(ax, title, middle_boxes):
    """middle_boxes: list of (x, text, color) drawn left->right after clients."""
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 9)
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold", color="#1A5276", pad=10)

    # Left column: the three farm/user clients
    clients = [
        (7.0, "Farmer's Android Phone\n(Flutter App)"),
        (4.5, "Raspberry Pi Camera\n(pi_camera.py)"),
        (2.0, "ESP32 Node /\nPython IoT Simulator"),
    ]
    cx = 2.3
    for cy, text in clients:
        box(ax, cx, cy, text, CLIENT)

    # Middle/right chain
    prev_x, prev_y = cx, 4.5
    for i, (mx, text, color) in enumerate(middle_boxes):
        my = 4.5
        box(ax, mx, my, text, color)
        if i == 0:
            # connect all three clients into the first middle box
            for cy, _ in clients:
                lbl = "HTTPS" if abs(cy - 7.0) < 0.1 else None
                arrow(ax, cx, cy, mx, my, label=lbl)
        else:
            two = (color == DB)  # backend <-> database is two-way
            arrow(ax, prev_x, my, mx, my, two_way=two)
        prev_x, prev_y = mx, my


fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9))

# (a) Development
draw_panel(
    ax1,
    "(a) Development Deployment (Current)",
    [
        (6.3, "ngrok Tunnel\n(public HTTPS URL)", TUNNEL),
        (9.8, "FastAPI Backend\n(localhost:8000,\ndev laptop)", SERVER),
        (13.0, "Supabase\nPostgreSQL\n(Cloud, EU)", DB),
    ],
)

# (b) Production
draw_panel(
    ax2,
    "(b) Production Deployment (Planned, Post-FYP)",
    [
        (8.0, "Cloud VPS Server\n(Railway / AWS EC2)\nFastAPI + uvicorn", SERVER),
        (12.5, "Supabase\nPostgreSQL\n(Cloud)", DB),
    ],
)

fig.suptitle("Figure 4.2: Development and Production Deployment Architectures",
             fontsize=13, fontweight="bold", y=0.99)
fig.tight_layout(rect=[0, 0, 1, 0.97])
fig.savefig("figure_4_2_deployment.png", dpi=170, bbox_inches="tight")
print("Saved: figure_4_2_deployment.png")
