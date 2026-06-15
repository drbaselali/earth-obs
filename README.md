Earth Climate Observations

A collection of geospatial and environmental data analysis applications using Python. 

Repository Structure
data/ - datasets
notebooks/ - exploratory analysis
src/ - reusable code
figures/ - generated plots and maps

Current Project titled "Earth Climate Analysis Using Environmental and Economic Indicators"

The goal of the project is to employ several ML and data analysis tools via Python to answer the following questions:
1- Which countries emit the most CO2 per person?
2- What is the relationships between GDP, population, forests, agriculture, renewable energy consumption and emissions?
3- Can countries be clustered into specific related profiles?
4- Which factors are strongly correlated with emission?

The project currently uses the following data from World Bank Open Data:
CO2 contribution per capita: https://data.worldbank.org/indicator/EN.GHG.CO2.PC.CE.AR5   
CO2 global contribution: https://data.worldbank.org/indicator/EN.GHG.CO2.MT.CE.AR5
Forest area: https://data.worldbank.org/indicator/AG.LND.FRST.ZS
Agricultural area: https://data.worldbank.org/indicator/AG.LND.AGRI.ZS
Renewable energy consumption: https://data.worldbank.org/indicator/EG.FEC.RNEW.ZS
GDP per capita: https://data.worldbank.org/indicator/NY.GDP.MKTP.KD
Population: https://data.worldbank.org/indicator/SP.POP.TOTL

Project Workflow:
1- Data gathering and clearning
2- Statistical and correlation estimations
3- Visualisations
4- Supervised and unsupervised learning analysis

Tools and Components:
1- Data Processing using pandas, geopandas
2- Statistics, scatter plots, heatmaps and geographic mapping using seaborn and matplotlip
3- HDBSCAN clustering and GLOSH outlier detection (unsupervised learning) using hdbscan library in Python
4- Random forest and feature importance (supervised learning) using sklearn library in Python


Author

Dr. Basel Ali
