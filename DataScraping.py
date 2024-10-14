import requests
from bs4 import BeautifulSoup
import csv

url_masini = []
with open('linkuri_masini.txt', 'r') as file:
    for line in file:
        url_masini.append(line.strip())
date_masini = []

for url in url_masini:
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        titlu = soup.find('h3', class_='offer-title big-text ezl3qpx2 ooa-ebtemw er34gjf0').text.strip()

        an_km_motor_combustibil = soup.find('p',
                                            class_='ezl3qpx3 ooa-1i4y99d er34gjf0').text.strip()

        pret = soup.find('h3', class_='offer-price__number eqdspoq4 ooa-o7wv9s er34gjf0').text.strip()

        detalii = an_km_motor_combustibil
        info_list = detalii.split(' · ')
        anul = info_list[0]
        kilometrajul = info_list[1]
        capacitatea_motorului = info_list[2]
        tipul_de_combustibil = info_list[3]

        date_masini.append({
            'Titlu': titlu,
            'Anul': anul,
            'Kilometrajul': kilometrajul,
            'Capacitatea motorului': capacitatea_motorului,
            'Tipul de combustibil': tipul_de_combustibil,
            'Preț': pret
        })

with open('detalii_masini.csv', mode='w', newline='', encoding='utf-8') as fisier:
    writer = csv.DictWriter(fisier, fieldnames=['Titlu', 'Anul', 'Kilometrajul', 'Capacitatea motorului',
                                                'Tipul de combustibil', 'Preț'])
    writer.writeheader()
    for masina in date_masini:
        writer.writerow(masina)
