set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off

SELECT 
	
	DISTINCT FORMAT ( CONVERT(datetime, convert(varchar(10), Fakturadato)), 'MM') AS maned,
	FORMAT ( CONVERT(datetime, convert(varchar(10), Fakturadato)), 'yyyy') AS ar,
	Butikk,
	Strekkode,
	Navnr,
	SUM(Antall) as 'Antall',
	SUM(u_mva) AS 'u_mva',
	SUM(m_mva) AS 'm_mva',
	SUM(DB) AS 'DB'
  
  FROM [F0001].[dbo].[PRODUKTRANSER_ALLE]
  WHERE 
	
  Fakturadato <> 0
  AND 
  Transaksjonstype = 1
  AND 
 
  NAVnr <> ''
  
  
  GROUP BY
  FORMAT ( CONVERT(datetime, convert(varchar(10), Fakturadato)), 'MM'),
  FORMAT ( CONVERT(datetime, convert(varchar(10), Fakturadato)), 'yyyy'),
	Butikk,
	Strekkode,
	NAVnr
go
    quit