import shapefile
import pyproj
from time import time
import collections
import datetime
import mysql.connector

from localconfig import configs

def getRegion(point, shapes, records):
    for shape, record in zip(shapes, records):
        if shapefile.ring_contains_point(shape.points, point):
            return record[0 if len(record) == 1 else 4]
    return None


if __name__ == '__main__':
    mydb = mysql.connector.connect(host = "192.168.0.223", user="wca", database="wca")
    cursor = mydb.cursor()

    for current_config in configs:

        print(f'Running {current_config['country']}/{current_config['name']}')
        time_start = time()

        sf = shapefile.Reader(current_config['filePath'])

        shapes = sf.shapes()
        records = sf.records()

        comp_regions = {}


        proj_wgs84 = pyproj.Proj(projparams='GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]')
        proj_local = pyproj.Proj(projparams=current_config['projParams'])
        transformer = pyproj.Transformer.from_proj(proj_from=proj_wgs84, proj_to=proj_local)

        cursor.execute("select id, countryId, latitude, longitude, year, month, day from Competitions;")

        for id, countryId, lat, lon, year, month, day in cursor:
            lat /= 1_000_000
            lon /= 1_000_000
            date = datetime.datetime(year, month, day)
            #print(id, countryId, lat, lon)
            if countryId == current_config['country'] and date < datetime.datetime.now():
                current_region = getRegion(transformer.transform(lat, lon), shapes, records)
                if current_region:
                    comp_regions[id] = current_region

        print(f"Loaded comp regions in: {time() - time_start}s")

        all_regions = set([region[0 if len(region) == 1 else 4] for region in records])
        person_comps = collections.defaultdict(set)

        cursor.execute('select competitionId, personId from Results;')

        for comp_name, person in cursor:
            if comp_name in comp_regions:
                person_comps[person].add(comp_name)

        print(f"Loaded person comps in: {time() - time_start}s")

        person_regions = collections.defaultdict(set)

        for person in person_comps:
            for comp in person_comps[person]:
                person_regions[person].add(comp_regions[comp])

        all_persons = list(person_comps.keys())
        all_persons.sort(key=lambda x: len(person_regions[x]), reverse=True)

        for person in all_persons[:current_config['printNumber']]:
            count = len(person_regions[person])
            missing = all_regions.difference(person_regions[person])
            print(f"{person}: {count}/{len(all_regions)}", end='')
            if len(missing) and len(missing) <= current_config['maxMissing']:
                print(f", missing: {missing}")
            else:
                print()

    