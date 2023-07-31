regions = open('export_solved.csv')
comp_regions = {}
for comp in regions:
    parts = comp.rstrip('\n').split(',')
    comp_regions[parts[0]] = parts[4]
#print(comp_regions)

f = open('WCA_export_Results.tsv')

osoby = {}
for line in f:
    parts = line.rstrip('\n').split('\t')
    if parts[16] == 'Poland':
        comp = parts[0]
        person = parts[7]
        if comp in comp_regions:
            if person not in osoby:
                osoby[person] = []
            if comp not in osoby[person]:
                osoby[person].append(comp)

osoby_regions = []
for osoba in osoby:
    regions = []
    for comp in osoby[osoba]:
        region = comp_regions[comp]
        if region not in regions:
            regions.append(region)
    osoby_regions.append([osoba, len(regions), regions])

all_regions = ['Łódzkie', 'Kujawsko-Pomorskie', 'Podlaskie', 'Pomorskie', 'Wielkopolskie', 'Śląskie', 'Podkarpackie', 'Dolnośląskie', 'Mazowieckie', 'Lubelskie', 'Małopolskie', 'Świętokrzyskie', 'Zachodniopomorskie', 'Opolskie', 'Warmińsko-Mazurskie', 'Lubuskie']
osoby_regions.sort(key=lambda x: x[1], reverse = True)
counts = {}
for person in osoby_regions:
    if person[1] > 12:
        missing = []
        for region in all_regions:
            if region not in person[2]:
                missing.append(region)
        print(person[0], person[1], missing)
    if person[1] not in counts:
        counts[person[1]] = 0
    counts[person[1]] += 1
for x in range(17, 0, -1):
    if x in counts:
        print(f"{x}: {counts[x]}")


