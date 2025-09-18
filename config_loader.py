import shapefile
import collections
from shapely.geometry import Point, shape
from renames import *

def get_local_configs(cursor, log):
    global_sf = shapefile.Reader('borders/World_Administrative_Divisions.zip')

    countries_dynamic_configs = []
    cursor.execute("select distinct(countryId) from Competitions where STR_TO_DATE(CONCAT(year,'-',month,'-',day), '%Y-%m-%d') < CURRENT_DATE() and cancelled != 1 and countryId not like 'X%' order by countryId;")
    for country in cursor:
        country_name = country[0]
        if country_name in renames:
            if renames[country_name] is not None:
                country_name = renames[country_name]
            else:
                log(f'{country_name} is missing from the global shapefile.', 'error')
                continue
        local_region_name = ''
        regions = set()
        name_counts = collections.defaultdict(int)
        max_occurences = 0
        for region in global_sf.records():
            #print(country, region[3], region[7])
            if region[3] == country_name:
                name_counts[region[7]] += 1
                max_occurences = max(max_occurences, name_counts[region[7]])
                regions.add(region[2])
        for name in name_counts:
            if name_counts[name] == max_occurences:
                local_region_name = name

        regions_count = len(regions)

        new_config = {
            'name': local_region_name,
            'path_name': local_region_name.replace(' ', '_').lower(),
            'country': country[0],
            'filePath': None,
            'projParams': 'PROJCS["WGS_1984_Web_Mercator_Auxiliary_Sphere",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator_Auxiliary_Sphere"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],PARAMETER["Standard_Parallel_1",0.0],PARAMETER["Auxiliary_Sphere_Type",0.0],UNIT["Meter",1.0]]',
            'printNumber': 100,
            'namePos': 2
        }
        if not local_region_name:
            print(country_name)
        countries_dynamic_configs.append(new_config)

    return countries_dynamic_configs


