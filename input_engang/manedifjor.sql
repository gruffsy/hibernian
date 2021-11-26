set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off

	

DECLARE @last_year AS VARCHAR(100)=convert(varchar, dateadd(year, -1, getdate()), 112)
DECLARE @this_month AS VARCHAR(100)=convert(varchar, datepart(month, getdate()), 112)

select 
butikk,
Klient,

sum(m_mva) AS 'mmoms',
sum(u_mva) AS 'umoms',
	sum(u_mva - kostnad)AS 'db',
	sum(u_mva - kostnad)/sum(u_mva) as 'dg',
	count(distinct Ordrenummer) as 'antord',
	sum(m_mva)/count(distinct Ordrenummer) as 'prord'


from f0001.dbo.PRODUKTRANSER_ALLE
where 

fakturadato <= cast(@last_year as int)
and 
--FORMAT ( CONVERT(datetime, convert(varchar(10), Fakturadato)), 'MM') = datepart(month, getdate())
substring(   Cast(fakturadato as varchar(10)),5,2) = @this_month

and transaksjonstype = 1
and Ordretype = 3


group by
butikk,
Klient

union all
select
	'Totalt' As 'butikk',
9999,

sum(m_mva) AS 'mmoms',
sum(u_mva) AS 'umoms',
	sum(u_mva - kostnad)AS 'db',
	sum(u_mva - kostnad)/sum(u_mva) as 'dg',
	count(distinct Ordrenummer) as 'antord',
	sum(m_mva)/count(distinct Ordrenummer) as 'prord'
	from f0001.dbo.PRODUKTRANSER_ALLE
where 
fakturadato <= cast(@last_year as int)
and 
substring(   Cast(fakturadato as varchar(10)),5,2) =substring(Cast(datepart(month, cast(getdate() as Date)) as varchar(10)),1,2) 
and transaksjonstype = 1
and Ordretype = 3

order by klient
	
	
for json auto
