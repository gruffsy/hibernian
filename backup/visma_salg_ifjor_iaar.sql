set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off

SELECT 
  fakturadato,
  butikk,
  Klient,
  CAST(sum(m_mva) AS INT) AS 'mmoms',
  CAST(sum(u_mva) AS INT) AS 'umoms',
  CAST(sum(u_mva - kostnad) AS INT) AS 'db',
  CAST(ROUND(sum(u_mva - kostnad)/sum(u_mva),2) AS FLOAT) as 'dg',
  count(distinct Ordrenummer) as 'antord',
  CAST((sum(m_mva)/count(distinct Ordrenummer)) AS INT) as 'prord'
FROM f0001.dbo.PRODUKTRANSER_ALLE
WHERE 
  fakturadato BETWEEN '20220101' AND convert(varchar, getdate(), 112)
  AND Fakturadato <> 0
  AND transaksjonstype = 1
  AND Ordretype = 3
GROUP BY
  fakturadato,
  butikk,
  Klient 
order by
fakturadato,
klient

for json auto
