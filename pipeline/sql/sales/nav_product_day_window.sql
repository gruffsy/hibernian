select
    se.[Item No_] as [Item No_],
    i.[Description] as [Description],
    i.[Item Category] as [Item Category],
    i.[Retail Product Group] as [Retail Product Group],
    th.[Date] as [fakturadato],
    SUM(se.[Quantity]) * -1 as [antall],
    SUM(se.[Net Amount]) * -1 AS [umoms],
    (SUM(se.[Net Amount]) - SUM(se.[Cost Amount])) * -1 AS [db],
    CASE
        WHEN SUM(se.[Net Amount]) = 0 THEN 0
        ELSE CAST(ROUND((SUM(se.[Net Amount]) - SUM(se.[Cost Amount])) / SUM(se.[Net Amount]), 4) AS float)
    END AS [dg]
from [mf_trans_sales_entry__hib] se
inner join [mf_transaction_header__hib] th
    on th.[Store No_] = se.[Store No_]
    and th.[POS Terminal No_] = se.[POS Terminal No_]
    and th.[Transaction No_] = se.[Transaction No_]
left join [mf_items] i
    on se.[Item No_] = i.[No_]
where th.[Transaction Type] = 2
    and th.[Receipt No_] is not null
    and th.[Customer Account] = 0
    and th.[Date] >= ?
    and th.[Date] < ?
group by
    se.[Item No_],
    i.[Description],
    i.[Item Category],
    i.[Retail Product Group],
    th.[Date]
order by
    th.[Date] desc,
    [umoms] desc,
    [Item No_] asc
