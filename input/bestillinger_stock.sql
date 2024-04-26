set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off
SELECT [ProdNo]
     , [Descr]
     , [NoInvoAb]
    ,DATEPART(WEEK, CAST(DelDt AS DATE)) AS uke
  ,DATEPART(YEAR, CAST(DelDt AS DATE)) AS år
FROM [F0015].[dbo].[OrdLn]
where trtp = 6
and NoInvoAb <> 0
for json auto
