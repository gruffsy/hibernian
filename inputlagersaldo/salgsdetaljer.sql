set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off

	
SELECT TOP 1
	
  butikk,
	Navnr AS ItemNo,
ferdigmeldtdato,
sum(antall) as 'antall',
sum(m_mva) AS 'mmoms',
sum(u_mva) AS 'umoms',
sum(u_mva - kostnad) AS 'db',
CASE WHEN Ordretype = 1
               THEN sum(m_mva)
          END AS Kreditt

	


from f0001.dbo.PRODUKTRANSER_ALLE
where 
transaksjonstype = 1
and antall <> 0
and produktnr <> 'a1'
and Kundeprisgruppe <> 4
and ferdigmeldtdato >= 20220101

group by
butikk,
navnr,
ferdigmeldtdato,
ordretype
	

