set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian;
set
    noexec off

select
    'Bamble' as butikk,
    convert(varchar, th.[Date], 112) as Dato, 
    [Item No_] as ItemNo,
    SUM(Quantity)*-1 as 'antall',
    sum([Total Rounded Amt_])*-1 as mmoms,
    sum(se.[Net Amount])*-1 as umoms,
    sum(se.[Net Amount])*-1-sum(se.[Cost Amount])*-1 as db,
     [Customer Account] as Kreditt
from
    
    [Hibernian Retail$Trans_ Sales Entry] se
    inner join [Hibernian Retail$Transaction Header] th
    on 
       th.[Store No_]=se.[Store No_] and
        th.[POS Terminal No_]=se.[POS Terminal No_] and
        th.[Transaction No_]=se.[Transaction No_]
    INNER JOIN [Hibernian Retail$Store] s
    on s.No_=th.[Store No_]
where th.[Transaction Type]=2 
group by 
       [Item No_],
       th.[Date],
    [Customer Account]

go
quit

