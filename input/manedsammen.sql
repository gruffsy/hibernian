set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off


DECLARE @last_year AS VARCHAR(100)=concat(left(convert(varchar, dateadd(year, -1, getdate()), 112),4), '0101')
DECLARE @today as VARCHAR(100) = convert(varchar, dateadd(year, -1, getdate()), 112)


SELECT
	m1.butikk as 'butikk',

	FORMAT(m1.mmoms - m2.mmoms,'### ### ##0 kr') AS 'mmoms',
	FORMAT(m1.umoms - m2.umoms ,'### ### ##0 kr') AS 'umoms',
	FORMAT(m1.db - m2.db,'### ### ##0 kr') AS 'db',
	FORMAT(m1.dg - m2.dg, 'P1') as 'dg',
	FORMAT(m1.antord - m2.antord, '### ### ##0') as 'antord',
	FORMAT(m1.prord - m2.prord, '### ### ##0 kr') as 'prord'

from
	(


		select
			butikk,
			Klient,
			FORMAT(sum(m_mva),'### ### ##0 kr') AS 'mmoms',
			FORMAT(sum(u_mva),'### ### ##0 kr') AS 'umoms',
			FORMAT(sum(u_mva - kostnad),'### ### ##0 kr') AS 'db',
			FORMAT(sum(u_mva - kostnad)/sum(u_mva), 'P1') as 'dg',
			FORMAT(count(distinct Ordrenummer), '### ### ##0') as 'antord',
			FORMAT(sum(m_mva)/count(distinct Ordrenummer), '### ### ##0 kr') as 'prord'


		from f0001.dbo.PRODUKTRANSER_ALLE
		where 

fakturadato >= cast(@last_year as int)
			and fakturadato <= cast(@today as int)

			and
			transaksjonstype = 1
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
			FORMAT(sum(u_mva - kostnad)/sum(u_mva), 'P1') as 'dg',
			FORMAT(count(distinct Ordrenummer), '### ### ##0') as 'antord',
			FORMAT(sum(m_mva)/count(distinct Ordrenummer), '### ### ##0 kr') as 'prord'
		from f0001.dbo.PRODUKTRANSER_ALLE
		where 

fakturadato >= cast(@last_year as int)
			and fakturadato <= cast(@today as int)

			and
			transaksjonstype = 1
			and Ordretype = 3


) as m2
	cross join

	(




		select
			butikk,
			Klient,

			FORMAT(sum(m_mva),'### ### ##0 kr') AS 'mmoms',
			FORMAT(sum(u_mva),'### ### ##0 kr') AS 'umoms',
			FORMAT(sum(u_mva - kostnad),'### ### ##0 kr') AS 'db',
			FORMAT(sum(u_mva - kostnad)/sum(u_mva), 'P1') as 'dg',
			FORMAT(count(distinct Ordrenummer), '### ### ##0') as 'antord',
			FORMAT(sum(m_mva)/count(distinct Ordrenummer), '### ### ##0 kr') as 'prord'


		from f0001.dbo.PRODUKTRANSER_ALLE
		where 
substring(   Cast(fakturadato as varchar(10)),1,4) =substring(Cast(datepart(year, cast(getdate() as Date)) as varchar(10)),1,4)
			and
			substring(   Cast(fakturadato as varchar(10)),5,2) =substring(Cast(format(getdate(), 'MM')as varchar(10)),1,2)
			and Fakturadato <> 0
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
			FORMAT(sum(u_mva - kostnad)/sum(u_mva), 'P1') as 'dg',
			FORMAT(count(distinct Ordrenummer), '### ### ##0') as 'antord',
			FORMAT(sum(m_mva)/count(distinct Ordrenummer), '### ### ##0 kr') as 'prord'
		from f0001.dbo.PRODUKTRANSER_ALLE
		where 
substring(   Cast(fakturadato as varchar(10)),1,4) =substring(Cast(datepart(year, cast(getdate() as Date)) as varchar(10)),1,4)
			and
			substring(   Cast(fakturadato as varchar(10)),5,2) =substring(Cast(format(getdate(), 'MM')as varchar(10)),1,2)
			and Fakturadato <> 0
			and transaksjonstype = 1
			and Ordretype = 3


) as m1

where m1.butikk = m2.butikk
order by
	m1.klient


for json auto
