import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from functools import reduce
import numpy as np
import hdbscan
from sklearn.preprocessing import StandardScaler
from hdbscan import validity
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import seaborn as sns
import numpy as np
import pandas as pd
import hdbscan
from hdbscan import validity
import umap.umap_ as umap


# a function for clearning data and sorting entries
def load_indicator(path, value_name):

    df = pd.read_csv(path, skiprows=4)

    df.columns = df.columns.str.strip()

    year_cols = [c for c in df.columns if c.isdigit()]
    year_col = None
    for y in sorted(year_cols, reverse=True):
        if df[y].notna().sum() > 0:
            year_col = y
            break

    print(f"{value_name}: using year {year_col}")

    return df[["Country Name", "Country Code", year_col]].rename(
        columns={year_col: value_name}
    )


# datasets from predownloaded World Bank Open Data CSVs
co2_pc = load_indicator("CO2emission.csv", "co2_per_capita")

co2_global = load_indicator("CO2emissionglobalcontribution.csv", "co2_global")

population = load_indicator("populations.csv", "population")

gdp = load_indicator("gdp.csv", "gdp_per_capita")

renewables = load_indicator(
    "Renewable energy consumption (% of total final energy consumption).csv",
    "renewables",
)

forest = load_indicator("Forest area (% land area).csv", "forest_pct")

agri = load_indicator("Agricultural land (% of land area).csv", "agri_pct")


dfs = [co2_pc, population, gdp, renewables, forest, agri]

df = reduce(
    lambda left, right: pd.merge(
        left, right, on=["Country Name", "Country Code"], how="outer"
    ),
    dfs,
)


# statistical estimations
variables = [
    "co2_per_capita",
    "population",
    "gdp_per_capita",
    "renewables",
    "forest_pct",
    "agri_pct",
]

stats = pd.DataFrame(
    {
        "mean": df[variables].mean(),
        "median": df[variables].median(),
        "std": df[variables].std(),
        "skewness": df[variables].skew(),
    }
)

print("\nStatistics")
print(stats.round(2))

# plot styling global
plt.rcParams.update(
    {
        "font.size": 12,
        "axes.titlesize": 16,
        "axes.labelsize": 14,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
    }
)

# country boundaries
world = gpd.read_file(
    "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
)

print(world.columns)
world = world.merge(df, left_on="SOV_A3", right_on="Country Code", how="left")

# CO2 per capita plot
fig, ax = plt.subplots(figsize=(14, 6))

world.plot(
    column="co2_per_capita",
    cmap="Reds",
    legend=True,
    missing_kwds={"color": "lightgrey", "label": "No Data"},
    ax=ax,
)


ax.set_title("CO₂ Emissions Per Capita", fontsize=18)

ax.axis("off")

plt.tight_layout()
plt.savefig("co2_per_capita_map.png", dpi=300)

# scatter renw vs co2 pc
scatter_df = df.dropna(subset=["renewables", "co2_per_capita"])

plt.figure(figsize=(10, 6))

plt.scatter(scatter_df["renewables"], scatter_df["co2_per_capita"], alpha=0.7)

plt.xlabel("Renewable Energy Consumption (%)", fontsize=14)
plt.ylabel("CO₂ Emissions Per Capita", fontsize=14)
plt.title("Renewable Energy vs CO₂ Emissions Per Capita", fontsize=14)

plt.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig("renewables_vs_co2_scatter.png", dpi=300)
plt.show()


# stacked areas bar
land_df = (
    df[["Country Name", "forest_pct", "agri_pct"]]
    .dropna()
    .sort_values("forest_pct", ascending=False)
    .head(20)
)

plt.figure(figsize=(14, 6))

plt.bar(land_df["Country Name"], land_df["forest_pct"], label="Forest Area (%)")

plt.bar(
    land_df["Country Name"],
    land_df["agri_pct"],
    bottom=land_df["forest_pct"],
    label="Agricultural Land (%)",
)

plt.xticks(rotation=90)
plt.ylabel("Percentage of Land Area", fontsize=14)
plt.title("Forest Area vs Agricultural Land Area", fontsize=14)
plt.legend()

plt.tight_layout()
plt.savefig("forest_agri_stacked_bar.png", dpi=300)
plt.show()


# heatmap correlations
corr_vars = [
    "co2_per_capita",
    "population",
    "gdp_per_capita",
    "renewables",
    "forest_pct",
    "agri_pct",
]

corr_matrix = df[corr_vars].corr()

plt.figure(figsize=(8, 6))

sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", center=0, fmt=".2f")

plt.title("Correlation Heatmap of Environmental and Economic Indicators", fontsize=16)

plt.tight_layout()
plt.savefig("correlation_heatmap.png", dpi=300)
plt.show()


# hdbscan clustering
def run_hdbscan(cluster_vars, df, title_suffix):

    cluster_df = df[["Country Name"] + cluster_vars].dropna()

    scaler = StandardScaler()
    X = scaler.fit_transform(cluster_df[cluster_vars])

    best_score = -np.inf
    best_model = None
    best_params = None

    for min_cluster_size in range(4, 50):
        for min_samples in range(4, 50):

            model = hdbscan.HDBSCAN(
                min_cluster_size=min_cluster_size,
                min_samples=min_samples,
            )

            labels = model.fit_predict(X)

            if len(set(labels)) <= 1:
                continue

            score = validity.validity_index(X, labels)

            if score > best_score:
                best_score = score
                best_model = model
                best_params = (min_cluster_size, min_samples)

    cluster_df["cluster"] = best_model.labels_
    cluster_df["outlier_score"] = best_model.outlier_scores_

    print(f"\n===== {title_suffix} =====")
    print("Best parameters:", best_params)
    print("Best DBCV score:", round(best_score, 4))

    print("\nCluster sizes:")
    print(cluster_df["cluster"].value_counts().sort_index())

    print("\nCluster summary:")
    print(cluster_df.groupby("cluster")[cluster_vars].mean().round(2))

    reducer = umap.UMAP(
        n_neighbors=15,
        min_dist=0.1,
        random_state=42,
    )

    X_umap = reducer.fit_transform(X)

    cluster_df["UMAP1"] = X_umap[:, 0]
    cluster_df["UMAP2"] = X_umap[:, 1]

    plt.figure(figsize=(12, 8))

    sns.scatterplot(
        data=cluster_df,
        x="UMAP1",
        y="UMAP2",
        hue="cluster",
        palette="Set2",
        s=120,
        alpha=0.9,
    )

    plt.xlabel("UMAP Dimension 1", fontsize=14)
    plt.ylabel("UMAP Dimension 2", fontsize=14)
    plt.title("HDBSCAN Clusters (UMAP Projection)", fontsize=16)

    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()

    plt.savefig(f"HDBSCAN_Clusters_{title_suffix}.png", dpi=300)
    plt.show()

    # outlier plot
    plt.figure(figsize=(13, 10))

    scatter = plt.scatter(
        cluster_df["UMAP1"],
        cluster_df["UMAP2"],
        c=cluster_df["outlier_score"],
        cmap="Reds",
        s=120,
    )

    plt.colorbar(scatter, label="Outlier Score")
    plt.xlabel("UMAP Dimension 1", fontsize=14)
    plt.ylabel("UMAP Dimension 2", fontsize=14)
    plt.title(f"HDBSCAN Outlier Scores - {title_suffix}", fontsize=16)
    plt.tight_layout()

    plt.savefig(f"HDBSCAN_Outliers_{title_suffix}.png", dpi=300)
    plt.show()

    return cluster_df


# without renewables
cluster_vars_no_ren = [
    "co2_per_capita",
    "gdp_per_capita",
    "forest_pct",
    "agri_pct",
]

results_no_ren = run_hdbscan(cluster_vars_no_ren, df, "No_Renewables")


# with renewables
cluster_vars_with_ren = [
    "co2_per_capita",
    "gdp_per_capita",
    "renewables",
    "forest_pct",
    "agri_pct",
]

results_with_ren = run_hdbscan(cluster_vars_with_ren, df, "With_Renewables")

# random forest
features = [
    "population",
    "gdp_per_capita",
    "renewables",
    "forest_pct",
    "agri_pct",
]

rf_df = df[features + ["co2_per_capita"]].dropna()

X = rf_df[features]
y = rf_df["co2_per_capita"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

rf = RandomForestRegressor(n_estimators=500, random_state=42)

rf.fit(X_train, y_train)

y_pred = rf.predict(X_test)

print("R²:", r2_score(y_test, y_pred))
print("RMSE:", mean_squared_error(y_test, y_pred) ** 0.5)


# feature importance
importance = pd.DataFrame(
    {"feature": features, "importance": rf.feature_importances_}
).sort_values("importance", ascending=False)

print(importance)

plt.figure(figsize=(13, 10))

plt.barh(importance["feature"], importance["importance"])

plt.xlabel("Importance", fontsize=14)
plt.title("Random Forest Feature Importance", fontsize=14)

plt.tight_layout()
plt.savefig("feature_importance.png", dpi=300)
plt.show()


# combined figure
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

sns.scatterplot(
    data=results_no_ren,
    x="UMAP1",
    y="UMAP2",
    hue="cluster",
    palette="Set2",
    s=80,
    ax=axes[0, 0],
    legend=False,
)

axes[0, 0].set_title("(A) HDBSCAN - Without Renewables", fontsize=13)
axes[0, 0].set_xlabel("UMAP1")
axes[0, 0].set_ylabel("UMAP2")


sns.scatterplot(
    data=results_with_ren,
    x="UMAP1",
    y="UMAP2",
    hue="cluster",
    palette="Set2",
    s=80,
    ax=axes[0, 1],
    legend=False,
)

axes[0, 1].set_title("(B) HDBSCAN - With Renewables", fontsize=13)
axes[0, 1].set_xlabel("UMAP1")
axes[0, 1].set_ylabel("UMAP2")

sc = axes[1, 0].scatter(
    results_with_ren["UMAP1"],
    results_with_ren["UMAP2"],
    c=results_with_ren["outlier_score"],
    cmap="Reds",
    s=80,
)

axes[1, 0].set_title("(C) HDBSCAN Outlier Scores", fontsize=13)
axes[1, 0].set_xlabel("UMAP1")
axes[1, 0].set_ylabel("UMAP2")

cbar = plt.colorbar(sc, ax=axes[1, 0])
cbar.set_label("Outlier Score")

importance_sorted = importance.sort_values("importance")

axes[1, 1].barh(
    importance_sorted["feature"], importance_sorted["importance"], color="steelblue"
)

axes[1, 1].set_title("(D) Random Forest Feature Importance", fontsize=13)
axes[1, 1].set_xlabel("Importance")


plt.suptitle("Earth Climate Analysis: Clustering & Predictive Modeling", fontsize=16)

plt.tight_layout()
plt.savefig("final_summary_figure.png", dpi=300, bbox_inches="tight")
plt.show()
