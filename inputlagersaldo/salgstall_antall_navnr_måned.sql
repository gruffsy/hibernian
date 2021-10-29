set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off

SELECT 
	
	DISTINCT FORMAT ( CONVERT(datetime, convert(varchar(10), Fakturadato)), 'MM') AS Month,
	FORMAT ( CONVERT(datetime, convert(varchar(10), Fakturadato)), 'yyyy') AS Year,
	Navnr As ItemNo,
	SUM(Antall) as 'SalesQty'
	
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
  FORMAT ( CONVERT(datetime, convert(varchar(10), Fakturadato)), 'MM'),
  FORMAT ( CONVERT(datetime, convert(varchar(10), Fakturadato)), 'yyyy'),
datepart(week, CONVERT(datetime, convert(varchar(10), Ferdigmeldtdato))),
	NAVnr
go
    quit