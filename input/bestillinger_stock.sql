set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off
SELECT 
    [ProdNo] as 'Prodno', 
    [Descr], 
    [NoInvoAb], 
    CASE 
        WHEN [DelDt] > 0 
        THEN 
            CAST(DATEPART(ISO_WEEK, CONVERT(DATE, CAST([DelDt] AS VARCHAR(8)), 112)) AS VARCHAR(2))
            + '/'
            + CAST(DATEPART(YEAR, CONVERT(DATE, CAST([DelDt] AS VARCHAR(8)), 112)) AS VARCHAR(4))
        ELSE 
            NULL
    END AS [Week_Year]
FROM 
    [F0015].[dbo].[OrdLn]
WHERE 
    trtp = 6
    AND NoInvoAb <> 0
for json auto
