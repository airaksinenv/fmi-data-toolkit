# fmi-data-toolkit (Customer project 1)
-Valtteri Airaksinen TTV20SAI / Valio Primary production team 

This repository contains code and documentation about fetching data from fmi (Finnish Meterological Institute) for the use of a neural network.

### Course requirements
- 200h of documented work.
- All documentation will be done in english.
- The following documents must be created during the course:
    - [Project plan](documents/project-plan.pdf) (6-10 pages, inc. front page, table of contents, etc.)
    - [Project requirements](documents/project-requirements.pdf) (inc. required timetable and required amount of work.)
    - Use case diagram (min. 7 use cases)
    - Sequence diagrams (min. 4pcs)
    - Final report
    - Lessons Learned -document
- The course must contain following elements:
    - Customer needs, which have been described in the documentation
    - Use of AI in the issue
    - Implementing a web environment for AI (e.g. feeding data to the AI, reporting results or collecting data.)

### Required data
1km*1km hila data
-   3h data (date, h temp, prec, wind_speed, rel_humid)
-   monthly data (date_start, date_end, temp_avg, temp_min, temp_max, prec, wind_speed_avg, wind_speed_max, wind_dir_avg, rel_humid_avg, rel_humid_max, rel_humid_min, global_rad, vapour_press, snow_depth)
-   daily temp sum
-   daily (temp_avg	temp_min, temp_max, prec, wind_speed_avg, wind_speed_max, wind_dir_avg, rel_humid_avg, rel_humid_max, rel_humid_min, global_rad, vapour_press, snow_depth)

1)	Asiakasrajapinnasta löytyy tuntidatana (9kk taaksepäin): tuottaja (kriging_suomi_hourly) ja parametrit (Temperature, Humidity, WindSpeedMS, Precipitation1h.) 

2)	Asiakasrajapinnasta löytyy tuntidatana (3vrk taaksepäin): tuottaja(roadkriging_suomi) ja parametrit (Friction, DewPointDeficit, DewPoint, Temperature, RoadTemperature, GroundTemperature, Visibility, Humidity, Precipitation1h, WindSpeedMS, MaximumWind)

3)	Asiakas rajapinnasta 3h dataa (7kk taaksepäin):  tuottaja (kriging_suomi_synop) ja parametrit (Temperature, Humidity, Precipitation3h, Evaporation, PrecipitationForm, Pressure, WindSpeedMS)

4)	Asiakas rajapinnasta löytyy vrk:n lumensyvyyttä (10vrk taaksepäin):  tuottaja (kriging_suomi_snow) ja parametri hämäävästi(WaterEquivalentOfSnow)

5)	Asiakasrajapinnasta löytyy vrk-datana (9kk taaksepäin): tuottaja (kriging_suomi_daily) ja parametrit (Precipitation24h, MaximumTemperature24h, MinimumTemperature24h, MaximumWind, DailyMeanTemperature, MinimumGroundTemperature06, DailyGlobalRadiation, VolumetricSoilWaterLayer1) 

6) lämpötilasumma (laskeeko Luke sen itse vai Ilmatieteenlaitos) tuottaja: kriging_suomi_kasvukausi ja parametri: EffectiveTemperatureSum

Ehtisitkö auttamaan nopsaan lisää? Olisi mahtavaa, jos saisin näihin kysymyksiini vastauksen niin nopeasti kuin mahdollista. Ekaa yritän paraikaa epätoivoissani työstää.
-	Mistä löytyy lumensyvyys? En ole onnistunut saamaan näillä mitään ulos:
o	kriging_suomi_snow
o	WaterEquivalentOfSnow

-	Sain imuroitua tietoa kriging_suomi_daily’stä, mutta en ymmärrä kaikkien muuttujien nimeä enkä sitä, että osasinko imuroida kaikki meille tarpeelliset muuttujat sieltä. Dataa tuli ainakin paljon! 
o	time-alkuisia muuttujia
o	air_temperature-alkuisia muuttujia
o	lämpötila ilmeisesti Kelvineitä?
o	olisiko kannattanut käyttää crs-parametriä? En käyttänyt
o	olisiko kannattanut käyttää bbox-parametriä? En käyttänyt, mutta tietoa tuli paljon)
-	Pahoittelutu, eipä ole näemmä lumensyvyyttä konfattu gridiksi (ei toimi netcdf, grib1 ja Grib2 haku). Timeserihaut toimii ja voitte käyttää aluetta (bbox): esim: https://data.fmi.fi/fmi-apikey/xxx/timeseries?bbox=25.5017659868161,67.5026234249509,26.0182259817672,68.0073738863099&param=utctime%2CDailyMeanTemperature,latlon&model=kriging_suomi_daily&format=json&timeformat=sql&starttime=2025-04-14T00%3A00%3A00&endtime=2025-05-15T00%3A00%3A00&timestep=data&precision=double 
-	
-	Ja lumensyvyys: https://data.fmi.fi/fmi-apikey/xxx/timeseries?bbox=25.5017659868161,67.5026234249509,26.0182259817672,68.0073738863099&param=utctime%2CWaterEquivalentOfSnow,latlon&model=kriging_suomi_snow&format=json&timeformat=sql&starttime=2025-04-14T00%3A00%3A00&endtime=2025-05-15T00%3A00%3A00&timestep=data&precision=double


-	Mistä löytyy Luken datasta löytyvät muuttujat 1*1km hilalla 
o	wind_speed_avg (täytyy laskea)
o	wind_speed_max (ks. Tuotaja Kriging daily 18.3)
o	wind_dir_avg Tätäpä ei muuten ole rajapinnassa, ennusteen lähtöhetki antaa kyllä ihan hyvän arvion suunnasta. Voinee olla usein jopa parempi kuin havaintojen perusteella tehty analyysi. 
o	rel_humid_avg pitää laskea
o	rel_humid_max pitää laskea
o	rel_humid_min voi laskea tuntiarvoista löytyy myös tuottaja roadkriging_suomi_daily18 ja parametri: MinimumHumidity
o	vapour_press
o	snow_depth
o	lämpötilasumma (laskeeko Luke sen itse vai Ilmatieteenlaitos) tuottaja: kriging_suomi_kasvukausi ja parametri: EffectiveTemperatureSum
Vastasin suurimpaan osaan näistä jo aiemmin, etupäässä 18.3 viestissä. 
