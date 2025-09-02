import shapefile
import pyproj
from time import time, ctime
import collections
import datetime
import mysql.connector
import os
import shutil
from shapely.geometry import Point, shape

from dbsecrets import *
from localconfig import configs

global logtext

def getRegion(point, shapes, records, namePos):
    potential_results = []
    for polygon, record in zip(shapes, records):
        if point.within(polygon):
            potential_results.append(record[namePos])
    if len(potential_results) > 1:
        log("SIUR NA OGÓLNYM")
        log(potential_results)
    if potential_results:
        return potential_results[0]
    return None

def table_head(elements):
    row = '<thead><tr>'
    for element in elements:
        row += f'<th>{element}</th>'
    row += '</tr></thead>'
    return row

def table_row(elements):
    row = '<tr>'
    for element in elements:
        row += f'<td>{element}</td>'
    row += '</tr>'
    return row

def link(title, url):
    return f'<a href="{url}">{title}</a>'

def log(text):
    global logtext
    print(text)
    logtext += f'<p>{text}</p>'


if __name__ == '__main__':
    mydb = None
    if SECRET_PASSWORD:
        mydb = mysql.connector.connect(host = SECRET_HOST, user = SECRET_USER, database = SECRET_DATABASE, password = SECRET_PASSWORD)
    else:
        mydb = mysql.connector.connect(host = SECRET_HOST, user = SECRET_USER, database = SECRET_DATABASE)
    cursor = mydb.cursor()
    if os.path.isdir('output'):
        shutil.rmtree('output')

    logtext = ''
    log(f'Started script at {ctime()}')
           
    for current_config in configs:

        log(f'Running {current_config['country']}/{current_config['name']}')
        time_start = time()
        try:
            sf = shapefile.Reader(current_config['filePath'])   
        except FileNotFoundError:
            log(f'File for {current_config['country']}/{current_config['name']} is missing.')
            continue

        shapes = [shape(x) for x in sf.shapes() if x.shapeType != 0]
        records = sf.records()

        comp_regions = {}


        proj_wgs84 = pyproj.Proj(projparams='GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]')
        proj_local = pyproj.Proj(projparams=current_config['projParams'])
        transformer = pyproj.Transformer.from_proj(proj_from=proj_wgs84, proj_to=proj_local)

        cursor.execute("select id, countryId, latitude, longitude, year, month, day from Competitions where cancelled != 1;")

        comp_dates = {}

        for id, countryId, lat, lon, year, month, day in cursor:
            lat /= 1_000_000
            lon /= 1_000_000
            date = datetime.datetime(year, month, day)
            #print(id, countryId, lat, lon)
            if countryId == current_config['country'] and date < datetime.datetime.now():
                comp_dates[id] = date
                current_region = getRegion(Point(transformer.transform(lat, lon)), shapes, records, current_config['namePos'])
                if current_region == 'Rondonia':
                    print(id)
                if current_region:
                    comp_regions[id] = current_region

        log(f"Loaded comp regions in: {time() - time_start}s")

        all_regions = set([region[current_config['namePos']] for region in records])
        person_comps = collections.defaultdict(set)

        cursor.execute('select competitionId, personId from Results;')

        for comp_name, person in cursor:
            if comp_name in comp_regions:
                person_comps[person].add(comp_name)

        log(f"Loaded person comps in: {time() - time_start}s")

        person_regions = collections.defaultdict(set)

        finished_people_last_comps = {}

        for person in person_comps:
            for comp in sorted(person_comps[person], key=lambda x: comp_dates[x]):
                person_regions[person].add(comp_regions[comp])
                if len(person_regions[person]) == len(all_regions) and person not in finished_people_last_comps:
                    finished_people_last_comps[person] = comp

        all_persons = list(person_comps.keys())
        all_persons.sort(key=lambda x: (-len(person_regions[x]), comp_dates[finished_people_last_comps[x]] if x in finished_people_last_comps else None))
        
        folder_path = os.path.join('output', current_config['country'])
        file_path = os.path.join('output', current_config['country'], current_config['path_name']+'.html')
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)
        with open(file_path, 'w', encoding='utf-8') as file:
            with open('templates/region_ranking.html') as template:
                template_text = ''.join([line for line in template])
                start, end = template_text.split('%')
                file.write(start)
                file.write('<table>')
                head = ['Position', 'Person', 'Region count']
                render_missing = False
                render_completed = False
                if all_persons:
                    if len(all_regions.difference(person_regions[all_persons[0]])) <= current_config['maxMissing']:
                        render_missing = True
                        head.append(f'Missing (up to {current_config['maxMissing']})')
                    if len(person_regions[all_persons[0]]) == len(all_regions):
                        render_completed = True
                        head.append('Completed at')
                file.write(table_head(head))
                last_count = 0
                last_last_comp = ''
                last_pos = 0
                for pos, person in enumerate(all_persons[:current_config['printNumber']]):
                    count = len(person_regions[person])
                    cursor.execute("select name from Persons where id=%(id)s and subid=1 limit 1;", {"id": person})
                    person_name = cursor.fetchall()[0][0]
                    if count != last_count or (count == len(all_regions) and last_last_comp != finished_people_last_comps[person]):
                        last_pos = pos + 1
                    last_count = count
                    last_last_comp = finished_people_last_comps[person] if person in finished_people_last_comps else ''

                    row = [last_pos, link(person_name, f'https://www.worldcubeassociation.org/persons/{person}'), f'{count}/{len(all_regions)}']

                    if render_missing:
                        missing = all_regions.difference(person_regions[person])
                        missing_text = ''
                        if len(missing) <= current_config['maxMissing']:
                            missing_with_comp = []
                            missing_without_comp = []
                            for region in missing:
                                if region not in comp_regions.values():
                                    missing_without_comp.append(region)
                                else:
                                    missing_with_comp.append(region)

                            missing_with_comp.sort()
                            missing_without_comp.sort()
                            if len(missing_without_comp):
                                missing_without_comp[0] = '<span class="noComp">' + missing_without_comp[0]
                                if len(missing_with_comp):
                                    missing_with_comp[0] = '</span>' + missing_with_comp[0]
                                else:
                                    missing_without_comp[-1] += '</span>'
                            missing_text = ', '.join(missing_without_comp + missing_with_comp)
                        row.append(missing_text)

                    if render_completed:
                        final_comp_text = ''
                        if count == len(all_regions):
                            final_comp = finished_people_last_comps[person]
                            cursor.execute("select name from Competitions where id=%(id)s", {"id": final_comp})
                            final_comp_name = cursor.fetchall()[0][0]
                            final_comp_text = link(final_comp_name, f'https://www.worldcubeassociation.org/competitions/{final_comp}')
                        row.append(final_comp_text)
                        
                    file.write(table_row(row))
                file.write('</table>')
                file.write(end)

    # Generate menu file
    countries = collections.defaultdict(list)
    for config in configs:
        countries[config['country']].append(config)

    with open('output/index.html', 'w', encoding='utf-8') as menufile:
        with open('templates/menu_file.html') as template:
            template_text = ''.join([line for line in template])
            start, end = template_text.split('%')
            menufile.write(start)
            for country in sorted(list(countries.keys())):
                menufile.write(f'<h1>{country}</h1>')
                for config in countries[country]:
                    country = config['country']
                    path = config['path_name']
                    name = config['name']
                    menufile.write('<p>')
                    menufile.write(link(name, f'{country}/{path}.html'))
                    menufile.write('</p>')
            menufile.write(end)

    log(f'Stopped script at {ctime()}')

    # Generate log file
    with open('output/log.html', 'w', encoding='utf-8') as logfile:
        with open('templates/log_file.html') as template:
            template_text = ''.join([line for line in template])
            start, end = template_text.split('%')
            logfile.write(start)
            logfile.write(logtext)
            logfile.write(end)

    