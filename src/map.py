import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Load city data
df = pd.read_csv("data/cities.csv")

# Create geometry column
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["lon"], df["lat"]),
    crs="EPSG:4326"
)

# Load world boundaries
world = gpd.read_file(
    gpd.datasets.get_path("naturalearth_lowres")
)

# Plot
fig, ax = plt.subplots(figsize=(16, 8))

world.plot(
    ax=ax,
    color="lightgray",
    edgecolor="white"
)

gdf.plot(
    ax=ax,
    color="red",
    markersize=20
)

plt.title("Cities")
plt.tight_layout()

plt.savefig("figures/map.png", dpi=300)

plt.show()
