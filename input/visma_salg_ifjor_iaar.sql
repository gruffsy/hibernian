SELECT 
  fakturadato,
  butikk,
  Klient,
  sum(m_mva) AS 'mmoms',
  sum(u_mva) AS 'umoms',
  sum(u_mva - kostnad) AS 'db',
  CAST((sum(u_mva - kostnad)/sum(u_mva)) AS DECIMAL(5,2)) as 'dg',
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
