set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian;
set
    noexec off

select
	CONVERT(INT, CONVERT(VARCHAR, th.[Date], 112)) as 'fakturadato',
	'Bamble' as 'butikk', 
	7 as 'Klient',
    cast(sum([Total Rounded Amt_])*-1 as int) as 'mmoms',
    cast(sum(se.[Net Amount])*-1 as int) as 'umoms',
    cast(sum(se.[Net Amount])*-1-sum(se.[Cost Amount])*-1 as int) as 'db',
	cast(sum(se.[Net Amount]-se.[Cost Amount])/sum(se.[Net Amount]) AS DECIMAL(5,2)) as 'dg',
	count(distinct th.[Receipt No_]) as 'antord',
    cast(sum(-[Total Rounded Amt_])/count(distinct th.[Receipt No_]) as int) as 'prord'
from
      	[Hibernian Retail$Trans_ Sales Entry] se
inner join [Hibernian Retail$Transaction Header] th 
on 
	th.[Store No_]=se.[Store No_] and 
   	th.[POS Terminal No_]=se.[POS Terminal No_] and 
   	th.[Transaction No_]=se.[Transaction No_] 
INNER JOIN [Hibernian Retail$Store] s 
on
	s.No_=th.[Store No_]

LEFT JOIN [Hibernian Retail$Customer] c
on 
       th.[Customer No_] = c.No_ 
where 	th.[Transaction Type]=2 
	and th.[Entry Status] in (0,2)
	-- and th.[Date] = convert(varchar, getdate(), 112)
and 
	CONVERT(INT, CONVERT(VARCHAR, th.[Date], 112)) BETWEEN 20220101 AND convert(varchar, getdate(), 112)
	and nullif(th.[Receipt No_],'') is not null

and (
        c.[Customer Price Group] is null 
        or 
        c.[Customer Price Group] <> 'INTERNT'
        )
	--and [Customer Account] = 0
group by
	th.[Date]
order by
	th.[Date]
for json auto


