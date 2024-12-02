import shapefile
import pyproj
from time import time
import collections

def getRegion(point, shapes, records):
    for shape, record in zip(shapes, records):
        if shapefile.ring_contains_point(shape.points, point):
            return record[4]
    return None


if __name__ == '__main__':
    time_start = time()

    sf = shapefile.Reader('wojewodztwa.zip')

    shapes = sf.shapes()
    records = sf.records()

    comp_regions = {}

    proj_wgs84 = pyproj.Proj(projparams='GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]')
    proj_mercator = pyproj.Proj(projparams='PROJCS["ETRS_1989_Poland_CS92",GEOGCS["GCS_ETRF2000-PL",DATUM["D_ETRF2000_Poland",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",-5300000.0],PARAMETER["Central_Meridian",19.0],PARAMETER["Scale_Factor",0.9993],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]')
    transformer = pyproj.Transformer.from_proj(proj_from=proj_wgs84, proj_to=proj_mercator)

    with open('WCA_export/WCA_export_Competitions.tsv', encoding='utf-8') as compsfile:
        for row in compsfile:
            data = row.rstrip('\n').split('\t')
            if data[0] != 'id':
                id = data[0]
                countryId = data[3]
                lat = int(data[10]) / 1_000_000
                lon = int(data[11]) / 1_000_000
                #print(id, countryId, lat, lon)
                if countryId == "Poland":
                    comp_regions[id] = getRegion(transformer.transform(lat, lon), shapes, records)

    print(f"Loaded comp regions in: {time() - time_start}s")

    all_regions = set([region[4] for region in records])    
    person_comps = collections.defaultdict(set)

    with open('WCA_export/WCA_export_Results.tsv', encoding='utf-8') as resultsfile:
        for row in resultsfile:
            data = row.rstrip('\n').split('\t')
            comp_name = data[0]
            if comp_name != 'competitionId':
                if comp_name in comp_regions:
                    person = data[7]
                    person_comps[person].add(comp_name)

    print(f"Loaded person comps in: {time() - time_start}s")

    person_regions = collections.defaultdict(set)

    for person in person_comps:
        for comp in person_comps[person]:
            person_regions[person].add(comp_regions[comp])

    all_persons = list(person_comps.keys())
    all_persons.sort(key=lambda x: len(person_regions[x]), reverse=True)
    
    for person in all_persons[:50]:
        count = len(person_regions[person])
        missing = all_regions.difference(person_regions[person])
        print(f"{person}: {count}/{len(all_regions)}", end='')
        if len(missing) and len(missing) < 10:
            print(f", missing: {missing}")
        else:
            print()
