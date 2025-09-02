configs = [
    {
        'name': 'Województwa',
        'path_name': 'wojewodztwa',
        'country': 'Poland',
        'filePath': 'borders/Poland/wojewodztwa.zip',
        'projParams': 'PROJCS["ETRS_1989_Poland_CS92",GEOGCS["GCS_ETRF2000-PL",DATUM["D_ETRF2000_Poland",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",-5300000.0],PARAMETER["Central_Meridian",19.0],PARAMETER["Scale_Factor",0.9993],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]',
        'printNumber': 100,
        'maxMissing': 10,
        'namePos': 4
    },
    {
        'name': 'Powiaty',
        'path_name': 'powiaty',
        'country': 'Poland',
        'filePath': 'borders/Poland/powiaty.zip',
        'projParams': 'PROJCS["ETRS_1989_Poland_CS92",GEOGCS["GCS_ETRF2000-PL",DATUM["D_ETRF2000_Poland",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",-5300000.0],PARAMETER["Central_Meridian",19.0],PARAMETER["Scale_Factor",0.9993],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]',
        'printNumber': 100,
        'maxMissing': 350,
        'namePos': 4
    },
    {
        'name': 'Dzielnice Warszawy',
        'path_name': 'dzielnice_warszawy',
        'country': 'Poland',
        'filePath': 'borders/Poland/dzielnice.zip',
        'projParams': 'PROJCS["ETRS_1989_Poland_CS92",GEOGCS["GCS_ETRF2000-PL",DATUM["D_ETRF2000_Poland",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",-5300000.0],PARAMETER["Central_Meridian",19.0],PARAMETER["Scale_Factor",0.9993],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]',
        'printNumber': 100,
        'maxMissing': 10,
        'namePos': 0
    },
    {
        'name': 'Länder',
        'path_name': 'lander',
        'country': 'Germany',
        'filePath': 'borders/Germany/land_neu.zip', # Here i had to manually edit the .dbf file inside the zip, because the file i got from the website has AIDS and had ['Brandenburg'] instead of just Brandenburg
        'projParams': 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]',
        'printNumber': 100,
        'maxMissing': 10,
        'namePos': 2
    },
    {
        'name': 'States and territories',
        'path_name': 'states',
        'country': 'USA',
        'filePath': 'borders/USA/states.zip',
        'projParams': 'GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137,298.257222101]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]',
        'printNumber': 100,
        'maxMissing': 20,
        'namePos': 5
    }

]