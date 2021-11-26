set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off

	
select 
butikk,
Klient,

FORMAT(sum(m_mva),'### ### ##0 kr') AS 'mmoms',
FORMAT(sum(u_mva),'### ### ##0 kr') AS 'umoms',
	FORMAT(sum(u_mva - kostnad),'### ### ##0 kr') AS 'db',
	FORMAT(sum(u_mva - kostnad)/sum(u_mva), 'P') as 'dg',
	FORMAT(count(distinct Ordrenummer), '### ### ##0') as 'antord',
	FORMAT(sum(m_mva)/count(distinct Ordrenummer), '### ### ##0 kr') as 'prord'


from f0001.dbo.PRODUKTRANSER_ALLE
where 
substring(   Cast(fakturadato as varchar(10)),5,2) =substring(Cast(datepart(year, cast(getdate() as Date)) as varchar(10)),5,2)
and transaksjonstype = 1
and Ordretype = 3


group by
butikk,
Klient

union all
select
	'Totalt' As 'butikk',
9999,

FORMAT(sum(m_mva),'### ### ##0 kr') AS 'mmoms',
FORMAT(sum(u_mva),'### ### ##0 kr') AS 'umoms',
	FORMAT(sum(u_mva - kostnad),'### ### ##0 kr') AS 'db',
	FORMAT(sum(u_mva - kostnad)/sum(u_mva), 'P') as 'dg',
	FORMAT(count(distinct Ordrenummer), '### ### ##0') as 'antord',
	FORMAT(sum(m_mva)/count(distinct Ordrenummer), '### ### ##0 kr') as 'prord'
	from f0001.dbo.PRODUKTRANSER_ALLE
where 
substring(   Cast(fakturadato as varchar(10)),5,2) =substring(Cast(datepart(year, cast(getdate() as Date)) as varchar(10)),5,2) 
and transaksjonstype = 1
and Ordretype = 3

order by
klient
	
	
	
for json auto
