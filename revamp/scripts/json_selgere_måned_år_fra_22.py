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
monthly_sales = []
yearly_sales = defaultdict(lambda: {"total_sales": 0, "db_total": 0})

for sale in sales_data:
    seller_name = sale["navn"]
    total_sales = int(sale["umoms"].split()[0].replace("kr", "").replace(" ", ""))
    db = int(sale["db"].split()[0].replace("kr", "").replace(" ", ""))
    month, year = get_month_year(sale["fakturadato"])
    butikk = sale["butikk"]
    
    # Oppdater månedlig sammenfatning
    monthly_sale = {
        "måned": month,
        "år": year,
        "navn": seller_name,
        "umoms": sale["umoms"],
        "db": sale["db"],
        "butikk": butikk
    }
    monthly_sales.append(monthly_sale)
    
    # Oppdater årlig sammenfatning
    yearly_sales[seller_name]["total_sales"] += total_sales
    yearly_sales[seller_name]["db_total"] += db

# Lagre månedlig salg per selger i JSON-fil
with open('../publish/salg_pr_selger_fra_22_pr_måned.json', 'w', encoding='utf-8') as f:
    json.dump(monthly_sales, f, ensure_ascii=False, indent=4)

# Lagre årlig salg per selger i JSON-fil
yearly_sales_list = [{"år": year, "navn": seller, "umoms": f"{data['total_sales']:,d} kr", "db": f"{data['db_total']:,d} kr", "butikk": ""} for seller, data in yearly_sales.items() for year in yearly_sales[seller]]

with open('../publish/salg_pr_selger_fra_22_pr_år.json', 'w', encoding='utf-8') as f:
    json.dump(yearly_sales_list, f, ensure_ascii=False, indent=4)
