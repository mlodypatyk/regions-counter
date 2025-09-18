import shapefile
import pyproj
import collections
import datetime
import mysql.connector
import os
import pickle
import requests
import json
from time import time, ctime
from shapely.geometry import Point, shape

from dbsecrets import SECRET_HOST, SECRET_DATABASE, SECRET_PASSWORD, SECRET_USER
from localconfig import configs
from renames import renames
from config_loader import get_local_configs

global LOGTEXT

def getRegion(point, shapes, records, namePos):
    potential_results = []
    for polygon, record in zip(shapes, records):
        if point.within(polygon):
            potential_results.append(record[namePos])
    if len(potential_results) > 1:
        log('SIUR NA OGÓLNYM', 'error')
        log(potential_results, 'error')
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

def log(text, logclass = None):
    print(text)
    global LOGTEXT
    for line in str(text).split('\n'):
        if logclass:
            LOGTEXT += f'<p class="{logclass}">{line}</p>'
        else: 
            LOGTEXT += f'<p>{line}</p>'


if __name__ == '__main__':
    mydb = None
    if SECRET_PASSWORD:
        mydb = mysql.connector.connect(host = SECRET_HOST, user = SECRET_USER, database = SECRET_DATABASE, password = SECRET_PASSWORD)
    else:
        mydb = mysql.connector.connect(host = SECRET_HOST, user = SECRET_USER, database = SECRET_DATABASE)
    cursor = mydb.cursor()

    LOGTEXT = ''
    log(f'Started script at {ctime()}')

    cache = {}
    finished_regions = []
    comp_counts = {}
    if os.path.isfile('cache.pickle'):
        with open('cache.pickle', 'rb') as cache_file:
            cache = pickle.load(cache_file)
            finished_regions = cache['finished_regions']
            comp_counts = cache['comp_counts']
    log(json.dumps(cache, indent=4))

    global_sf = shapefile.Reader('borders/World_Administrative_Divisions.zip')

    local_configs = get_local_configs(cursor, log)

    # this is disgusting but idk how to do it otherwise
    cursor.execute('select id from Competitions where (cityName like "%Flere byer%" or cityName like "%Multiple%" or cityName like "%Múltiplas%" or cityName = "Kyiv and Kharkiv") and eventSpecs = "333fm" and countryId not like "X%"')
    multiple_locations_fmc = [comp[0] for comp in cursor]
           
    for current_config in local_configs + configs:

        log(f'Running {current_config['country']}/{current_config['name']}', 'countryStart')
        time_start = time()
        shapes = []
        records = []
        if current_config['filePath'] is not None:
            try:
                sf = shapefile.Reader(current_config['filePath'])   
            except FileNotFoundError:
                log(f'File for {current_config['country']}/{current_config['name']} is missing.')
                continue
            shapes = [shape(x) for x in sf.shapes() if x.shapeType != 0]
            records = sf.records()
        else:
            country_name = current_config['country']
            if country_name in renames:
                if renames[country_name] is not None:
                    country_name = renames[country_name]
                else:
                    log(f'{country_name} is missing from the global shapefile.')
                    continue
            for xshape, record in zip(global_sf.shapes(), global_sf.records()):
                if record[3] == country_name and xshape.shapeType != 0:
                    shapes.append(shape(xshape))
                    records.append(record)


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
            if countryId == current_config['country'] and date < datetime.datetime.now() and id not in multiple_locations_fmc:
                comp_dates[id] = date
                current_region = getRegion(Point(transformer.transform(lat, lon)), shapes, records, current_config['namePos'])
                if current_region:
                    comp_regions[id] = current_region

        log(f"Loaded comp regions in: {time() - time_start}s")


        folder_path = os.path.join('output', current_config['country'])
        file_path = os.path.join('output', current_config['country'], current_config['path_name']+'.html')

        identifier = current_config['country'] + current_config['name']

        if identifier in comp_counts and comp_counts[identifier] == len(comp_regions):
            #check if file exists
            if os.path.exists(file_path):
                log('Cached results, skipping', 'good')
                continue
        else:
            comp_counts[identifier] = len(comp_regions)

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
        

        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)

        if os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, 'w', encoding='utf-8') as file:
            with open('templates/region_ranking.html') as template:
                template_text = ''.join([line for line in template])
                start, end = template_text.split('%')
                file.write(start)
                head = ['Position', 'Person', 'Region count']
                render_completed = False
                show_completed_as_default = True
                if all_persons:
                    if len(person_regions[all_persons[0]]) == len(all_regions):
                        render_completed = True
                        finished_regions.append(f'{current_config['country']}{current_config['name']}')
                    if len(person_regions[all_persons[0]]) > len(all_regions)/2:
                        show_completed_as_default = False
                head.append(f'<span class="missing" style="display: {'none' if show_completed_as_default else ''};">Missing</span><span class="completed" style="display: {'' if show_completed_as_default else 'none'};">Completed</span>')
                if render_completed:
                    head.append('Completed at')
                file.write(f'<div class="topMenu"><input type="checkbox" id="tick"> Hide regions with no comps<input type="checkbox" id="tick2"{' checked' if show_completed_as_default else ''}> Toggle missing/completed</div>')
                file.write(f'<title>{current_config['country']}: {current_config['name']}</title>')
                file.write('<table>')
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

                    missing = all_regions.difference(person_regions[person])
                    missing_text = ''
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
                    missing_text = f'<span class="missing"{' style="display: none;"' if show_completed_as_default else ''}>' + ', '.join(missing_without_comp + missing_with_comp) + '</span>'

                    completed = list(person_regions[person])
                    completed.sort()
                    completed_text = f'<span class="completed"{' style="display: none;"' if not show_completed_as_default else ''}>' + ', '.join(completed) + '</span>'

                    row.append(missing_text + completed_text)

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
    for config in local_configs + configs:
        countries[config['country']].append(config)


    export_date = ''
    export_info = requests.request("GET", 'https://www.worldcubeassociation.org/api/v0/export/public')
    if export_info.ok:
        export_json = json.loads(export_info.text)
        export_date = export_json['export_date'][:10]
    

    with open('output/index.html', 'w', encoding='utf-8') as menufile:
        with open('templates/menu_file.html') as template:
            template_text = ''.join([line for line in template])
            start, end = template_text.split('%')
            menufile.write(start)
            menufile.write('<div class="header">')
            menufile.write(f'<span>This information is based on competition results owned and maintained by the World Cube Assocation, published at https://worldcubeassociation.org/results as of {export_date}.</span><br>')
            menufile.write(f'<span>Subdivions that someone completed (competed in all of them) are marked <span class="completed"><a>as such.</a></spanp></span>')
            menufile.write('</div>')
            for country in sorted(list(countries.keys())):
                menufile.write(f'<h1>{country}</h1>')
                for config in countries[country]:
                    country = config['country']
                    path = config['path_name']
                    name = config['name']
                    if f'{config['country']}{config['name']}' in finished_regions:
                        menufile.write('<p class="completed">')
                    else:
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
            logfile.write(LOGTEXT)
            logfile.write(end)

    # Write cache file
    with open('cache.pickle', 'wb') as cachefile:
        new_cache = {'finished_regions': finished_regions, 'comp_counts': comp_counts}
        pickle.dump(new_cache, cachefile)
    