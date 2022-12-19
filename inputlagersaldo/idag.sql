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
--ordretype,
sum(m_mva) AS 'mmoms',
sum(u_mva) AS 'umoms',
sum(u_mva - kostnad) AS 'db',
count(distinct Ordrenummer) as 'antord',
CASE WHEN Ordretype = 1
               THEN sum(m_mva)
          END AS Assignee

	


from f0001.dbo.PRODUKTRANSER_ALLE
where 
--Fakturadato <> 0
transaksjonstype = 1
--and Ordretype = 3
and antall <> 0
and produktnr <> 'a1'
and Kundeprisgruppe <> 4

group by
butikk,
--fakturadato,
ferdigmeldtdato,
Klient,
ordretype

order by
klient
	

