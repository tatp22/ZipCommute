# ZipCommute
Project using machine learning and zip codes to determine the cities with the fastest commute times

## How this works
This reads in 2 csv files, one containing location data of zip codes, and another one containing commute times of each zip codes. This then filters out the locations of zip codes not relating to cities, and then it preforms k-means to cluster the cities. Finally, it takes each zip code and gives it data, including local commute time, total cluster commute time, and also how it ranks in the country.

## To run
```python
git clone https://github.com/tatp22/ZipCommute .
cd ZipCommute
python main.py
```

## Details

### Clustering Algorithm
Todo...

### K-means
Todo...

### Other
Todo...