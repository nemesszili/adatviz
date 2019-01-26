import pandas as pd

import pycountry_convert

def country_name_to_country_code(row):
    if row.GEO == 'Kosovo':      #pycountry_convert does not now what Kosovo is, written by serbians maybe?
        return 'KSV'
    return pycountry_convert.country_name_to_country_alpha3(row.GEO)


def prepare_csv(csv_name):
    csv = pd.read_csv(csv_name)
    csv.replace(to_replace=r'Germany.*', value='Germany', regex=True,inplace=True)
    csv.replace(to_replace=r'France.*', value='France', regex=True,inplace=True)
    csv.replace(to_replace=r'Kosovo.*', value='Kosovo', regex=True,inplace=True)
    csv.replace(to_replace=r'Former.*', value='Macedonia', regex=True,inplace=True)
    csv['CODE'] = csv.apply(lambda row: country_name_to_country_code(row), axis=1)
    csv['Value'].replace(to_replace=r',', value='', regex=True, inplace=True)
    csv['Value'].replace(to_replace=r': ', value='', regex=True, inplace=True)
    csv['Category'] = csv[csv.columns[3]]
    csv.Value = pd.to_numeric(csv.Value, errors='coerce')
    csv.Value = csv.Value.fillna(0)
    return csv

population = prepare_csv('data/population.csv')
road_motorways = prepare_csv('data/roads_motorways.csv')
by_road_user = prepare_csv('data/1_by_road_user.csv')
by_vehicle = prepare_csv('data/2_by_vehicle.csv')
by_age = prepare_csv('data/3_by_age.csv')
vehicle_stock = prepare_csv('data/vehicle_stock.csv')
