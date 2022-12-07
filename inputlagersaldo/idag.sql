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
fakturadato,
Klient,

FORMAT(sum(m_mva),'### ### ##0 kr') AS 'mmoms',
FORMAT(sum(u_mva),'### ### ##0 kr') AS 'umoms',
	FORMAT(sum(u_mva - kostnad),'### ### ##0 kr') AS 'db',
	FORMAT(sum(u_mva - kostnad)/sum(u_mva), 'P1') as 'dg',
	FORMAT(count(distinct Ordrenummer), '### ### ##0') as 'antord',
	FORMAT(sum(m_mva)/count(distinct Ordrenummer), '### ### ##0 kr') as 'prord'


from f0001.dbo.PRODUKTRANSER_ALLE
where 
substring(   Cast(fakturadato as varchar(10)),1,4) >='2020'
and Fakturadato <> 0
and transaksjonstype = 1
and Ordretype = 3


group by
butikk,
fakturadato,
Klient

order by
klient
	

