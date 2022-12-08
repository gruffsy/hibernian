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
--fakturadato,
ferdigmeldtdato,
Klient,
ordretype,
sum(m_mva) AS 'mmoms',
sum(u_mva) AS 'umoms',
sum(u_mva - kostnad) AS 'db',
count(distinct Ordrenummer) as 'antord'

	


from f0001.dbo.PRODUKTRANSER_ALLE
where 
--Fakturadato <> 0
and transaksjonstype = 1
--and Ordretype = 3
and antall = 0

group by
butikk,
--fakturadato,
ferdigmeldtdato,
Klient,
ordretype

order by
klient
	

