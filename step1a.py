"""
Program 1: Wind Direction Map
Reads gps_data.csv and plots the balloon's route with bold arrows
showing direction of travel. Arrows are colored by speed.
"""
import csv
import math
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import matplotlib.cm as cm


def load_gps(path):
    """
    Load GPS data from a CSV file.

    Reads the file and extracts the time_s, latitude, and longitude
    columns into separate lists.

    Args:
        path (str): Path to the GPS CSV file.

    Returns:
        times (list): List of timestamps in seconds.
        lats (list):  List of latitude values.
        lons (list):  List of longitude values.
    """
    times, lats, lons = [], [], []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            times.append(float(row["time_s"]))
            lats.append(float(row["latitude"]))
            lons.append(float(row["longitude"]))
    return times, lats, lons


def plot_wind_map(lats, lons, step, title, out_path):
    """
    Plot a wind direction map showing the balloon's route with arrows.

    Args:
        lats (list):    List of latitude values from GPS data.
        lons (list):    List of longitude values from GPS data.
        step (int):     Number of rows between arrow start and end.
        title (str):    Title for the plot.
        out_path (str): File path to save the output figure.
    """
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 8))

    # Loop through the data to build arrow segments
    segments = []
    speeds = []
    for i in range(0, len(lats) - step, 2 * step):
        du = lons[i + step] - lons[i]
        dv = lats[i + step] - lats[i]
        speed = math.sqrt(du**2 + dv**2)
        segments.append(((lons[i], lats[i]), (lons[i + step], lats[i + step])))
        speeds.append(speed)

    # Normalize speeds and get colormap
    norm = mcolors.Normalize(vmin=min(speeds), vmax=max(speeds))
    colormap = cm.get_cmap("viridis")

    # Draw each arrow using ax.annotate so coordinates are in data space
    # (FancyArrowPatch by default uses display/figure coordinates, not data coords)
    for i, (start_pt, end_pt) in enumerate(segments):
        ax.annotate(
            "",
            xy=end_pt,           # arrow tip (lon, lat)
            xytext=start_pt,     # arrow tail (lon, lat)
            arrowprops=dict(
                arrowstyle="->",
                lw=2,
                color=colormap(norm(speeds[i])),
                mutation_scale=15,
            ),
        )

    # Add a colorbar
    mappable = cm.ScalarMappable(norm=norm, cmap=colormap)
    mappable.set_array([])
    fig.colorbar(mappable, ax=ax, label="Step magnitude (deg) — proxy for wind speed")

    # Set axis labels, title, and grid
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(title)
    ax.set_xlim(min(lons) - 0.05, max(lons) + 0.05)
    ax.set_ylim(min(lats) - 0.05, max(lats) + 0.05)
    ax.grid(True, linestyle="--", alpha=0.6)

    # Save the figure
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    print(f"Saved wind map to {out_path}")


def main():
    """
    Main function that loads GPS data and generates the wind map.
    """
    times, lats, lons = load_gps("gps_data.csv")

    plot_wind_map(
        lats, lons,
        step=10,
        title="Wind Direction Map",
        out_path="wind_map.png",
    )


if __name__ == "__main__":
    main()
