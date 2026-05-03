import tkinter as tk
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import time

@dataclass
class TrajectoryPoint:
    timestamp: float
    pdi_value: float
    epsilon: float
    site_id: str
    intervention_type: str
    is_revoked: bool = False
    is_gracefully_retired: bool = False

class LongitudinalPDIVisualizer:
    """
    Participant-controlled longitudinal trajectory visualization.
    Shows PDI evolution over time across sites and interventions,
    visually distinguishing between valid, pre-revocation, and revoked data.
    """

    def __init__(self, root: tk.Tk, participant_did: str):
        self.root = root
        self.participant_did = participant_did
        self.root.title(f"ARKHE OS - Sovereign Trajectory [{self.participant_did[:8]}...]")
        self.root.geometry("800x500")
        self.root.configure(bg="#0a0a0a")

        # Header
        self.header_frame = tk.Frame(self.root, bg="#0a0a0a")
        self.header_frame.pack(fill=tk.X, padx=20, pady=10)

        self.title_label = tk.Label(
            self.header_frame,
            text="Longitudinal PDI Evolution",
            font=("Courier", 18, "bold"),
            fg="#00aaff", bg="#0a0a0a"
        )
        self.title_label.pack(side=tk.LEFT)

        # Main Canvas for plotting
        self.canvas_width = 760
        self.canvas_height = 350
        self.canvas = tk.Canvas(
            self.root,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#111111",
            highlightthickness=1,
            highlightbackground="#333333"
        )
        self.canvas.pack(pady=10)

        # Legend
        self.legend_frame = tk.Frame(self.root, bg="#0a0a0a")
        self.legend_frame.pack(fill=tk.X, padx=20, pady=5)

        self._add_legend_item("Valid/Active", "#00ffcc")
        self._add_legend_item("Pre-Revocation (Historical)", "#aaaaaa", dash=(4, 4))
        self._add_legend_item("Revoked/Tombstoned", "#ff3333", cross=True)

        self.trajectory_data: List[TrajectoryPoint] = []

        # Draw axes
        self._draw_axes()

    def _add_legend_item(self, text: str, color: str, dash=None, cross=False):
        frame = tk.Frame(self.legend_frame, bg="#0a0a0a")
        frame.pack(side=tk.LEFT, padx=10)

        c = tk.Canvas(frame, width=30, height=20, bg="#0a0a0a", highlightthickness=0)
        c.pack(side=tk.LEFT)
        if cross:
            c.create_line(10, 5, 20, 15, fill=color, width=2)
            c.create_line(20, 5, 10, 15, fill=color, width=2)
        else:
            if dash:
                c.create_line(5, 10, 25, 10, fill=color, width=2, dash=dash)
            else:
                c.create_line(5, 10, 25, 10, fill=color, width=2)
                c.create_oval(12, 7, 18, 13, fill=color, outline=color)

        lbl = tk.Label(frame, text=text, font=("Courier", 10), fg="white", bg="#0a0a0a")
        lbl.pack(side=tk.LEFT)

    def _draw_axes(self):
        self.canvas.delete("axes")
        margin_x = 50
        margin_y = 30

        # Y-axis (PDI)
        self.canvas.create_line(
            margin_x, margin_y,
            margin_x, self.canvas_height - margin_y,
            fill="#555555", width=2, tags="axes"
        )
        self.canvas.create_text(
            margin_x - 30, margin_y,
            text="1.0", fill="#aaaaaa", font=("Courier", 10), tags="axes"
        )
        self.canvas.create_text(
            margin_x - 30, self.canvas_height - margin_y,
            text="0.0", fill="#aaaaaa", font=("Courier", 10), tags="axes"
        )
        self.canvas.create_text(
            margin_x - 30, self.canvas_height // 2,
            text="0.5", fill="#aaaaaa", font=("Courier", 10), tags="axes"
        )

        # X-axis (Time)
        self.canvas.create_line(
            margin_x, self.canvas_height - margin_y,
            self.canvas_width - margin_x, self.canvas_height - margin_y,
            fill="#555555", width=2, tags="axes"
        )

        # Mercy gap bounds visualization background
        # Normal PDI bounds might be mapped to acceptable epsilon boundaries
        # For visualization, let's just show a subtle background band for the 'ideal' dissolution threshold
        self.canvas.create_rectangle(
            margin_x, margin_y + (self.canvas_height - 2 * margin_y) * 0.05,
            self.canvas_width - margin_x, margin_y + (self.canvas_height - 2 * margin_y) * 0.15,
            fill="#002244", outline="", stipple="gray25", tags="axes"
        )
        self.canvas.create_text(
            self.canvas_width - margin_x - 60, margin_y + (self.canvas_height - 2 * margin_y) * 0.1,
            text="Dissolution\nThreshold", fill="#00aaff", font=("Courier", 8), tags="axes"
        )

    def load_trajectory(self, data: List[TrajectoryPoint]):
        """Load data and render the trajectory."""
        self.trajectory_data = sorted(data, key=lambda p: p.timestamp)
        self.render()

    def render(self):
        """Draw the longitudinal trajectory line and points."""
        self.canvas.delete("data")

        if not self.trajectory_data:
            return

        margin_x = 50
        margin_y = 30
        plot_width = self.canvas_width - 2 * margin_x
        plot_height = self.canvas_height - 2 * margin_y

        t_min = min(p.timestamp for p in self.trajectory_data)
        t_max = max(p.timestamp for p in self.trajectory_data)
        t_range = max(t_max - t_min, 1) # Prevent div by 0

        points_coords = []

        # Map data to canvas coordinates
        for p in self.trajectory_data:
            x = margin_x + ((p.timestamp - t_min) / t_range) * plot_width
            # Invert Y (0.0 is bottom, 1.0 is top)
            y = margin_y + (1.0 - p.pdi_value) * plot_height
            points_coords.append((x, y, p))

        # Draw connections
        for i in range(len(points_coords) - 1):
            x1, y1, p1 = points_coords[i]
            x2, y2, p2 = points_coords[i+1]

            # Determine line style based on states
            color = "#00ffcc" # Active
            dash = None

            if p1.is_revoked or p2.is_revoked:
                color = "#ff3333"
                dash = (2, 4)
            elif p1.is_gracefully_retired or p2.is_gracefully_retired:
                 color = "#aaaaaa"
                 dash = (4, 4)

            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=color, width=2, dash=dash, tags="data"
            )

        # Draw points
        for x, y, p in points_coords:
            radius = 4
            if p.is_revoked:
                # Draw red cross for tombstoned
                self.canvas.create_line(x-radius, y-radius, x+radius, y+radius, fill="#ff3333", width=2, tags="data")
                self.canvas.create_line(x+radius, y-radius, x-radius, y+radius, fill="#ff3333", width=2, tags="data")
            elif p.is_gracefully_retired:
                # Draw gray hollow circle for legacy/pre-revocation
                self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, outline="#aaaaaa", width=2, tags="data")
            else:
                # Draw solid cyan circle for active
                self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, fill="#00ffcc", outline="#00ffcc", tags="data")

            # Add site/intervention text sparingly
            if not p.is_revoked: # Only label non-revoked points
                 self.canvas.create_text(x, y - 15, text=f"{p.site_id}\n{p.intervention_type[:3]}", fill="#777777", font=("Courier", 7), tags="data")


def launch_visualization(participant_did: str, dummy_data: List[TrajectoryPoint]):
    root = tk.Tk()
    app = LongitudinalPDIVisualizer(root, participant_did)
    app.load_trajectory(dummy_data)
    # Automatically close after 1 second if running in a test/headless mode
    # root.after(1000, root.destroy)
    root.mainloop()

if __name__ == "__main__":
    now = time.time()
    day = 86400
    dummy = [
        TrajectoryPoint(now - 30*day, 0.95, 0.05, "SiteA", "tDCS"),
        TrajectoryPoint(now - 25*day, 0.92, 0.06, "SiteA", "tDCS"),
        TrajectoryPoint(now - 20*day, 0.88, 0.045, "SiteB", "NF", is_gracefully_retired=True), # This period was later revoked, but kept for legacy
        TrajectoryPoint(now - 15*day, 0.85, 0.05, "SiteB", "NF", is_revoked=True), # Tombstoned
        TrajectoryPoint(now - 10*day, 0.90, 0.07, "SiteC", "tDCS"),
        TrajectoryPoint(now - 5*day, 0.82, 0.055, "SiteC", "tDCS"),
        TrajectoryPoint(now, 0.78, 0.048, "SiteC", "tDCS")
    ]
    launch_visualization("did:arkhe:participant:0x1234abcd", dummy)
