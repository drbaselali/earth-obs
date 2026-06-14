import pandas as pd
import matplotlib.pyplot as plt

# Example dataset
years = [2015, 2016, 2017, 2018, 2019, 2020]
temperature = [14.1, 14.3, 14.5, 14.7, 14.8, 15.0]

df = pd.DataFrame({
    "Year": years,
    "Temperature": temperature
})

plt.plot(df["Year"], df["Temperature"])
plt.title("Example Temperature Trend")
plt.xlabel("Year")
plt.ylabel("Temperature")
plt.show()
