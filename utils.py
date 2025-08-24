import pandas as pd
import requests
import numpy as np

import xml.etree.ElementTree as ET
from datetime import datetime

def getSnowDepth(key, startdate, enddate, bbox):
    """
    Hakee lumensyvyysdatan Ilmatieteen laitoksen API:sta annetun avaimen, aikarajoitteen 
    ja alueen koordinaattien (bbox) perusteella. Funktio palauttaa pandas DataFrame -muotoisen 
    taulukon, joka sisältää aikaleiman (timestamp), leveyspiirin (latitude), pituuspiirin (longitude) 
    ja lumensyvyysarvon (snow_water_equivalent) kullekin koordinaatille. (HUOM. Ilmatieteen laitos säilöö tätä dataa vain kymmenen päivän ajan.)

    Parametrit:
    key (str): API-avain, joka tarvitaan tietojen hakemiseen.
    startdate (str): Hakuajan alku, muodossa 'YYYY-MM-DD'.
    enddate (str): Hakuajan loppu, muodossa 'YYYY-MM-DD'.
    bbox (list): Lista, joka määrittää alueen rajat muodossa [min_lon, min_lat, max_lon, max_lat].

    Palautus:
    pandas.DataFrame: DataFrame, joka sisältää seuraavat sarakkeet:
        - timestamp: Aikaleima (päivämäärä ja kellonaika)
        - latitude: Leveyspiiri
        - longitude: Pituuspiiri
        - snow_water_equivalent: Lumensyvyys (mm)
    """

    url = (
        f"https://data.fmi.fi/fmi-apikey/{key}/timeseries"
        f"?bbox={','.join(map(str, bbox))}"
        f"&param=utctime%2CWaterEquivalentOfSnow,latlon"
        f"&model=kriging_suomi_snow&format=json&timeformat=sql"
        f"&starttime={startdate}T00%3A00%3A00&endtime={enddate}T00%3A00%3A00"
        f"&timestep=data&precision=double"
    )

    # Lähetetään pyyntö ja tarkistetaan, ettei tullut virheitä
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    all_rows = []

    for entry in data:
        timestamp = entry["utctime"]

        # Käsitellään lumensyvyysarvot, muutetaan merkkijonosta taulukoksi
        snow_str = entry["WaterEquivalentOfSnow"].replace(" ", ",")
        snow_values = np.fromstring(snow_str.strip("[]"), sep=",")

        # Käsitellään koordinaatit, puhdistetaan merkkijonosta ja muunnetaan ne kellon ympäri
        latlon_raw = entry["latlon"].replace("[", "").replace("]", "").split()
        latlon_clean = [float(val.strip(",")) for val in latlon_raw]
        latlon_pairs = list(zip(latlon_clean[::2], latlon_clean[1::2]))

         # Tallennetaan tiedot listaan
        for (lat, lon), snow in zip(latlon_pairs, snow_values):
            all_rows.append({
                "timestamp": timestamp,
                "latitude": lat,
                "longitude": lon,
                "snow_water_equivalent": snow
            })

    # Muutetaan lista DataFrameksi ja palautetaan se
    df = pd.DataFrame(all_rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def getDailyWeatherData(key, startdate, enddate, bbox):
    """
    Hakee vuorokausittaista säätietoa Ilmatieteen laitoksen API:sta annetun API-avaimen, aikarajoitteen 
    ja koordinaattien (bbox) perusteella käyttäen mallia 'kriging_suomi_daily'. Palauttaa DataFramen, jossa on 
    timestamp, latitude, longitude ja useita sääparametreja.

    Parametrit:
    key (str): FMI API-avain.
    startdate (str): Alkamispäivä muodossa 'YYYY-MM-DD'.
    enddate (str): Loppupäivä muodossa 'YYYY-MM-DD'.
    bbox (list): Alue rajattuna [min_lon, min_lat, max_lon, max_lat].

    Palautus:
    pandas.DataFrame: Sarakkeet:
        - timestamp
        - latitude
        - longitude
        - Precipitation24h (mm)
        - MaximumTemperature24h (°C)
        - MinimumTemperature24h (°C)
        - MaximumWind (m/s)
        - DailyMeanTemperature (°C)
        - MinimumGroundTemperature06 (°C)
        - DailyGlobalRadiation (W/m²)
        - VolumetricSoilWaterLayer1 (%)
    """
    
    url = (
        f"https://data.fmi.fi/fmi-apikey/{key}/timeseries"
        f"?bbox={','.join(map(str, bbox))}"
        f"&param=utctime%2CPrecipitation24h%2CMaximumTemperature24h%2CMinimumTemperature24h%2CMaximumWind%2CDailyMeanTemperature%2CMinimumGroundTemperature06%2CDailyGlobalRadiation%2CVolumetricSoilWaterLayer1%2Clatlon"
        f"&model=kriging_suomi_daily&format=json&timeformat=sql"
        f"&starttime={startdate}T00%3A00%3A00&endtime={enddate}T00%3A00%3A00"
        f"&timestep=data&precision=double"
    )

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    all_rows = []

    for entry in data:
        timestamp = entry["utctime"]

        # Extract and parse values for each parameter
        prec_str = entry['Precipitation24h'].replace(" ", ",")
        prec_values = np.fromstring(prec_str.strip("[]"), sep=",")
        
        max_temp_str = entry['MaximumTemperature24h'].replace(" ", ",")
        max_temp_values = np.fromstring(max_temp_str.strip("[]"), sep=",")
        
        min_temp_str = entry['MinimumTemperature24h'].replace(" ", ",")
        min_temp_values = np.fromstring(min_temp_str.strip("[]"), sep=",")
        
        max_wind_str = entry['MaximumWind'].replace(" ", ",")
        max_wind_values = np.fromstring(max_wind_str.strip("[]"), sep=",")
        
        daily_mean_temp_str = entry['DailyMeanTemperature'].replace(" ", ",")
        daily_mean_temp_values = np.fromstring(daily_mean_temp_str.strip("[]"), sep=",")
        
        min_ground_temp_str = entry['MinimumGroundTemperature06'].replace(" ", ",")
        min_ground_temp_values = np.fromstring(min_ground_temp_str.strip("[]"), sep=",")
        
        global_rad_str = entry['DailyGlobalRadiation'].replace(" ", ",")
        global_rad_values = np.fromstring(global_rad_str.strip("[]"), sep=",")
        
        soil_water_str = entry['VolumetricSoilWaterLayer1'].replace(" ", ",")
        soil_water_values = np.fromstring(soil_water_str.strip("[]"), sep=",")
        
        # Parse latlon coordinates
        latlon_raw = entry["latlon"].replace("[", "").replace("]", "").split()
        latlon_clean = [float(val.strip(",")) for val in latlon_raw]
        latlon_pairs = list(zip(latlon_clean[::2], latlon_clean[1::2]))

        # Assuming all values have the same length and zipping them together
        for (lat, lon), prec, max_temp, min_temp, max_wind, daily_mean_temp, min_ground_temp, global_rad, soil_water in zip(
                latlon_pairs, prec_values, max_temp_values, min_temp_values, max_wind_values, daily_mean_temp_values,
                min_ground_temp_values, global_rad_values, soil_water_values):

            all_rows.append({
                "timestamp": timestamp,
                "latitude": lat,
                "longitude": lon,
                "Precipitation24h": prec,
                "MaximumTemperature24h": max_temp,
                "MinimumTemperature24h": min_temp,
                "MaximumWind": max_wind,
                "DailyMeanTemperature": daily_mean_temp,
                "MinimumGroundTemperature06": min_ground_temp,
                "DailyGlobalRadiation": global_rad,
                "VolumetricSoilWaterLayer1": soil_water
            })

    df = pd.DataFrame(all_rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

def getTempSum(key, startdate, enddate, bbox):
    """
    Hakee Ilmatieteen laitoksen API:sta lämpösummatietoa annetun API-avaimen, aikarajoitteen 
    ja koordinaattien (bbox) perusteella käyttäen mallia 'kriging_suomi_kasvukausi'. Palauttaa 
    pandas DataFrame -muotoisen taulukon, joka sisältää aikaleiman (timestamp), leveyspiirin (latitude), 
    pituuspiirin (longitude) ja lämpösumman (EffectiveTemperatureSum) kullekin koordinaatille.

    Parametrit:
    key (str): FMI API-avain.
    startdate (str): Alkamispäivä muodossa 'YYYY-MM-DD'.
    enddate (str): Loppupäivä muodossa 'YYYY-MM-DD'.
    bbox (list): Alue rajattuna [min_lon, min_lat, max_lon, max_lat].

    Palautus:
    pandas.DataFrame: Sarakkeet:
        - timestamp: Aikaleima (päivämäärä ja kellonaika)
        - latitude: Leveyspiiri
        - longitude: Pituuspiiri
        - EffectiveTemperatureSum: Lämpösumma (°C vuorokausittain kertynyt)
    """

    url = (
        f"https://data.fmi.fi/fmi-apikey/{key}/timeseries"
        f"?bbox={','.join(map(str, bbox))}"
        f"&param=utctime%2CEffectiveTemperatureSum,latlon"
        f"&model=kriging_suomi_kasvukausi&format=json&timeformat=sql"
        f"&starttime={startdate}T00%3A00%3A00&endtime={enddate}T00%3A00%3A00"
        f"&timestep=data&precision=double"
    )

    # Lähetetään pyyntö ja varmistetaan, ettei tullut virheitä
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    all_rows = []

    for entry in data:
        timestamp = entry["utctime"]

        # Käsitellään lämpösummatiedot, muutetaan merkkijono numeeriseksi taulukoksi
        tempsum_str = entry["EffectiveTemperatureSum"].replace(" ", ",")
        tempsum_values = np.fromstring(tempsum_str.strip("[]"), sep=",")

        # Käsitellään koordinaatit ja muunnetaan ne (lat, lon) pareiksi
        latlon_raw = entry["latlon"].replace("[", "").replace("]", "").split()
        latlon_clean = [float(val.strip(",")) for val in latlon_raw]
        latlon_pairs = list(zip(latlon_clean[::2], latlon_clean[1::2]))

        # Tallennetaan kaikki rivit tuloslistaan
        for (lat, lon), tempsum in zip(latlon_pairs, tempsum_values):
            all_rows.append({
                "timestamp": timestamp,
                "latitude": lat,
                "longitude": lon,
                "EffectiveTemperatureSum": tempsum
            })

    # Muodostetaan DataFrame ja palautetaan se
    df = pd.DataFrame(all_rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

# =========================================================================================================================

# Forecasts

def listAvailableParameters(key, lat, lon, starttime, endtime):
    """
    Queries FMI forecast WFS and lists all available observed parameters
    at the given location and time.

    Args:
        key (str): FMI API key
        lat (float): Latitude
        lon (float): Longitude
        starttime (str): ISO date (YYYY-MM-DD)
        endtime (str): ISO date (YYYY-MM-DD)

    Returns:
        set: A set of observed parameter names found in the response
    """
    url = (
        f"https://data.fmi.fi/fmi-apikey/{key}/wfs"
        "?request=getFeature"
        "&storedquery_id=fmi::forecast::harmonie::surface::point::timevaluepair"
        f"&latlon={lat},{lon}"
        f"&starttime={starttime}T00:00:00Z"
        f"&endtime={endtime}T23:59:59Z"
        "&timestep=60"
    )

    resp = requests.get(url)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)

    ns = {
        "wfs": "http://www.opengis.net/wfs/2.0",
        "om": "http://www.opengis.net/om/2.0",
        "gml": "http://www.opengis.net/gml/3.2",
        "wml2": "http://www.opengis.net/waterml/2.0",
        "sams": "http://www.opengis.net/samplingSpatial/2.0",
        "sf": "http://www.opengis.net/sampling/2.0",
        "gmd": "http://www.isotc211.org/2005/gmd",
    }

    observed_props = set()

    for prop in root.findall(".//om:observedProperty", ns):
        href = prop.attrib.get("{http://www.w3.org/1999/xlink}href")
        if href:
            observed_props.add(href.split("/")[-1])  # e.g., extract 't2m' from the URI

    print("Available observed parameters:")
    for p in sorted(observed_props):
        print(f" - {p}")

    return observed_props

def get_temperature_forecast(key, lat, lon, startdate, enddate):

    url = (
        f"https://data.fmi.fi/fmi-apikey/{key}/wfs"
        f"?request=getFeature"
        f"&storedquery_id=fmi::forecast::harmonie::surface::point::timevaluepair"
        f"&latlon={lat},{lon}"
        f"&starttime={startdate}T00:00:00Z"
        f"&endtime={enddate}T23:59:59Z"
        f"&parameters=Temperature"
    )

    response = requests.get(url)
    response.raise_for_status()

    root = ET.fromstring(response.content)

    ns = {
        "wfs": "http://www.opengis.net/wfs/2.0",
        "om": "http://www.opengis.net/om/2.0",
        "gml": "http://www.opengis.net/gml/3.2",
        "wml2": "http://www.opengis.net/waterml/2.0",
    }

    times = []
    temps = []

    for member in root.findall(".//wfs:member", ns):
        for meas in member.findall(".//wml2:MeasurementTimeseries", ns):
            for point in meas.findall(".//wml2:point", ns):
                time_elem = point.find(".//wml2:time", ns)
                value_elem = point.find(".//wml2:value", ns)

                if time_elem is not None and value_elem is not None:
                    time_str = time_elem.text
                    temp_str = value_elem.text

                    try:
                        time_dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                        temp_val = float(temp_str)
                    except Exception:
                        continue

                    times.append(time_dt)
                    temps.append(temp_val)

    if not times:
        return pd.DataFrame()

    df = pd.DataFrame({"time": times, "temperature": temps})
    df.set_index("time", inplace=True)

    daily_avg = df.resample("D").mean()

    # Muutetaan indeksi päivämääräksi ilman aikaa ja resetataan index sarakkeeksi
    daily_avg.index = daily_avg.index.date
    daily_avg.index.name = "date"
    daily_avg = daily_avg.reset_index()
    daily_avg["temperature"] = daily_avg["temperature"].round(1)

    daily_avg = daily_avg.rename(columns={"temperature": "avgTemp"})

    return daily_avg

def getTempSum_point(key, startdate, enddate, lat, lon):
    """
    Hakee Ilmatieteen laitoksen API:sta lämpösumman yhdelle pisteelle annetulla koordinaatilla.
    """

    url = (
        f"https://data.fmi.fi/fmi-apikey/{key}/timeseries"
        f"?latlon={lat},{lon}"
        f"&param=utctime%2CEffectiveTemperatureSum"
        f"&model=kriging_suomi_kasvukausi&format=json&timeformat=sql"
        f"&starttime={startdate}T00%3A00%3A00&endtime={enddate}T00%3A00%3A00"
        f"&timestep=data&precision=double"
    )

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    all_rows = []

    for entry in data:
        timestamp = entry["utctime"]
        tempsum = entry["EffectiveTemperatureSum"]  # float arvo suoraan

        latlon_raw = entry.get("latlon")
        if latlon_raw:
            latlon_clean = [float(x) for x in latlon_raw.replace("[", "").replace("]", "").split()]
            latlon_pairs = list(zip(latlon_clean[::2], latlon_clean[1::2]))
        else:
            latlon_pairs = [(lat, lon)]

        for (plat, plon) in latlon_pairs:
            all_rows.append({
                "date": timestamp,
                "tempSum": tempsum
            })

    df = pd.DataFrame(all_rows)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df

def virenwc_forecast(key, lat, lon, startdate, enddate):
    """
    Hakee Ilmatieteen laitoksen virenwc-ennusteen annetulle koordinaatille ja aikavälille.
    Palauttaa päivittäiset keskilämpötilat.
    """

    url = (
        f"https://data.fmi.fi/fmi-apikey/{key}/timeseries"
        f"?producer=virenwc"
        f"&latlon={lat},{lon}"
        f"&starttime={startdate}T00:00:00Z"
        f"&endtime={enddate}T23:59:59Z"
        f"&param=utctime,Temperature"
        f"&format=json&tz=utc"
    )

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # Support both dict and list responses
    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict) and "data" in data:
        entries = data["data"]
    else:
        print("⚠️ Unexpected JSON structure from FMI:")
        print(data)
        return pd.DataFrame()

    if not entries:
        print(f"⚠️ No forecast data returned for {lat}, {lon} between {startdate} and {enddate}")
        return pd.DataFrame()

    # Parse forecast data
    times = []
    temps = []

    for entry in entries:
        timestamp = entry.get("utctime")
        temperature = entry.get("Temperature")

        if timestamp and temperature is not None:
            try:
                # Handle malformed ISO strings like '20250618T090000'
                if 'T' in timestamp and len(timestamp) == 15:
                    timestamp = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]}T{timestamp[9:11]}:{timestamp[11:13]}:{timestamp[13:15]}"
                # Add timezone if missing
                if timestamp.endswith('Z'):
                    timestamp = timestamp.replace('Z', '+00:00')
                time_dt = datetime.fromisoformat(timestamp)
                temp_val = float(temperature)
            except Exception as e:
                print(f"⚠️ Parsing error: {e} (timestamp: {timestamp})")
                continue

            times.append(time_dt)
            temps.append(temp_val)

    if not times:
        print("⚠️ Forecast data parsed but contains no valid temperature entries.")
        return pd.DataFrame()

    df = pd.DataFrame({"time": times, "temperature": temps})
    df.set_index("time", inplace=True)

    # Resample to daily average temperature
    daily_avg = df.resample("D").mean()
    daily_avg.index = daily_avg.index.date
    daily_avg.index.name = "date"
    daily_avg = daily_avg.reset_index()
    daily_avg["avgTemp"] = daily_avg["temperature"].round(1)
    daily_avg = daily_avg.drop(columns="temperature")

    return daily_avg
