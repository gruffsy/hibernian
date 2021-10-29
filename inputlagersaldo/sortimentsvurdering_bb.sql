set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off

SELECT 
	
	DISTINCT FORMAT ( CONVERT(datetime, convert(varchar(10), Fakturadato)), 'yyyy') AS ar,
	NAVnr as 'ItemNo',
	SUM(Antall) as 'SalesQty',
	SUM(u_mva) AS 'SalesAmountExclVat',
	SUM(m_mva) AS 'SalesAmountInclVat',
	SUM(DB) AS 'BF'
  FROM 
  [F0001].[dbo].[varmepumper_ALLE]
  WHERE 
	FORMAT ( CONVERT(datetime, convert(varchar(10), Fakturadato)), 'yyyy') > 2019
AND
  Fakturadato <> 0
  AND 
  Transaksjonstype = 1
  AND 
  Kundeprisgruppe <> 4
  AND
  NAVnr <> ''
  
  
  GROUP BY
  	FORMAT ( CONVERT(datetime, convert(varchar(10), Fakturadato)), 'yyyy') AS ar,
	NAVnr
go
    quit