import geopandas as gpd
import matplotlib.pyplot as plt

# Built-in world dataset
world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

germany = world[world["name"] == "Germany"]

ax = germany.plot(
    color="lightblue",
    edgecolor="black",
    figsize=(6, 8)
)

plt.title("Germany")
plt.show()
