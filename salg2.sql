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
	7 as Klient,
    FORMAT(sum([Total Rounded Amt_])*-1, '### ### ##0 kr') as mmoms,
    FORMAT(sum(se.[Net Amount])*-1, '### ### ##0 kr') as umoms,
    FORMAT(sum(se.[Net Amount])*-1-sum(se.[Cost Amount])*-1, '### ### ##0 kr') as db,
	FORMAT(sum(se.[Net Amount]-se.[Cost Amount])/sum(se.[Net Amount]), 'P1') as dg,
	count(distinct th.[Receipt No_]) as antord,
    FORMAT(sum(-[Total Rounded Amt_])/count(distinct th.[Receipt No_]), '### ### ##0 kr') as prord,
	FORMAT(sum([Customer Account]), '### ### ##0 kr') as kreditt
from
      	[Megaflis Bamble AS$Trans_ Sales Entry] se 
inner join [Megaflis Bamble AS$Transaction Header] th 
on 
	th.[Store No_]=se.[Store No_] and 
   	th.[POS Terminal No_]=se.[POS Terminal No_] and 
   	th.[Transaction No_]=se.[Transaction No_] 
INNER JOIN [Megaflis Bamble AS$Store] s 
on
	s.No_=th.[Store No_]

LEFT JOIN [Megaflis Bamble AS$Customer] c
on 
       th.[Customer No_] = c.No_ 
where 	th.[Transaction Type]=2 
	and th.[Entry Status] in (0,2)
	and th.[Date] >= convert(varchar, getdate()-7, 112)
	and nullif(th.[Receipt No_],'') is not null

and (
        c.[Customer Price Group] is null 
        or 
        c.[Customer Price Group] <> 'INTERNT'
        )
group by
	th.[Date]
order by
	th.[Date]

go
quit

