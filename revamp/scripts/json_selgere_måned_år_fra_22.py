import json
from collections import defaultdict
from datetime import datetime

# Les inn JSON-dataene fra en fil
with open('../publish/salg_pr_selger_fra_22_pr_dag.json', 'r', encoding='utf-8') as f:
    sales_data = json.load(f)

# Funksjon for å omgjøre dato til måned og år
def get_month_year(date_int):
    date_str = str(date_int)
    date_obj = datetime.strptime(date_str, "%Y%m%d")
    month_str = date_obj.strftime("%B")
    year_str = date_obj.strftime("%Y")
    return month_str, year_str

# Sammenfatt salg per måned per selger
monthly_sales = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {"total_sales": 0, "db_total": 0, "butikk": ""})))
yearly_sales = defaultdict(lambda: defaultdict(lambda: {"total_sales": 0, "db_total": 0, "butikk": ""}))

for sale in sales_data:
    seller_name = sale["navn"]
    total_sales = int(sale["umoms"].replace("kr", "").replace(" ", "").replace("\xa0", ""))
    db = int(sale["db"].replace("kr", "").replace(" ", "").replace("\xa0", ""))
    month, year = get_month_year(sale["fakturadato"])
    butikk = sale["butikk"]
    
    # Oppdater månedlig sammenfatning
    monthly_sales[seller_name][year][month]["total_sales"] += total_sales
    monthly_sales[seller_name][year][month]["db_total"] += db
    monthly_sales[seller_name][year][month]["butikk"] = butikk
    
    # Oppdater årlig sammenfatning
    yearly_sales[seller_name][year]["total_sales"] += total_sales
    yearly_sales[seller_name][year]["db_total"] += db
    yearly_sales[seller_name][year]["butikk"] = butikk

# Lagre månedlig salg per selger i JSON-fil
monthly_sales_list = [{"måned": month, "år": year, "navn": seller, "umoms": f"{data['total_sales']:,d} kr", "db": f"{data['db_total']:,d} kr", "butikk": data["butikk"]} for seller, years in monthly_sales.items() for year, months in years.items() for month, data in months.items()]
monthly_sales_list_sorted = sorted(monthly_sales_list, key=lambda x: (-int(x['år']), -datetime.strptime(x['måned'], '%B').month, -int(x['umoms'].replace(' kr', '').replace(' ', '').replace(',', ''))))

with open('../publish/salg_pr_selger_fra_22_pr_måned.json', 'w', encoding='utf-8') as f:
    json.dump(monthly_sales_list_sorted, f, ensure_ascii=False, indent=4)

# Lagre årlig salg per selger i JSON-fil
yearly_sales_list = [{"år": year, "navn": seller, "umoms": f"{data['total_sales']:,d} kr", "db": f"{data['db_total']:,d} kr", "butikk": data["butikk"]} for seller, years in yearly_sales.items() for year, data in years.items()]
yearly_sales_list_sorted = sorted(yearly_sales_list, key=lambda x: (-int(x['år']), -int(x['umoms'].replace(' kr', '').replace(' ', '').replace(',', ''))))

with open('../publish/salg_pr_selger_fra_22_pr_år.json', 'w', encoding='utf-8') as f:
    json.dump(yearly_sales_list_sorted, f, ensure_ascii=False, indent=4)
