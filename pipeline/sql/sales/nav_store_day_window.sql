DECLARE @window_start_date date = ?;

SELECT
    CONVERT(INT, CONVERT(VARCHAR, th.[Date], 112)) AS fakturadato,
    CASE
        WHEN th.[Store No_] = 'S150' THEN 'Kristiansand'
        WHEN th.[Store No_] = 'S100' THEN 'Bamble'
        WHEN th.[Store No_] = 'S110' THEN 'Arendal'
        WHEN th.[Store No_] = 'S170' THEN 'Larvik'
        WHEN th.[Store No_] = 'S130' THEN 'Sandefjord'
        WHEN th.[Store No_] = 'S140' THEN 'Skien'
        WHEN th.[Store No_] = 'S160' THEN 'Tønsberg'
    END AS butikk,
    CASE
        WHEN th.[Store No_] = 'S150' THEN '2'
        WHEN th.[Store No_] = 'S100' THEN '7'
        WHEN th.[Store No_] = 'S110' THEN '4'
        WHEN th.[Store No_] = 'S170' THEN '6'
        WHEN th.[Store No_] = 'S130' THEN '5'
        WHEN th.[Store No_] = 'S160' THEN '3'
        WHEN th.[Store No_] = 'S140' THEN '0'
    END AS Klient,
    CAST(SUM(th.[Gross Amount]) * -1 AS int) AS mmoms,
    CAST(SUM(th.[Net Amount]) * -1 AS int) AS umoms,
    CAST(SUM(th.[Net Amount]) * -1 - SUM(th.[Cost Amount]) * -1 AS int) AS db,
    CASE
        WHEN SUM(th.[Net Amount]) = 0 THEN 0
        ELSE CAST(ROUND(SUM(th.[Net Amount] - th.[Cost Amount]) / SUM(th.[Net Amount]), 2) AS float)
    END AS dg,
    COUNT(DISTINCT th.[Receipt No_]) AS antord,
    CASE
        WHEN COUNT(DISTINCT th.[Receipt No_]) = 0 THEN 0
        ELSE CAST(SUM(-th.[Gross Amount]) / COUNT(DISTINCT th.[Receipt No_]) AS int)
    END AS prord
FROM [Megaflis_AS].[dbo].[mf_transaction_header__hib] th
LEFT JOIN [Hibernian Retail$Customer$437dbf0e-84ff-417a-965d-ed2bb9650972] c
    ON c.No_ = th.[customer no_]
WHERE th.[Transaction Type] = 2
  AND th.[Receipt No_] IS NOT NULL
  AND th.[Customer Account] = 0
  AND CAST(th.[Date] AS date) >= @window_start_date
GROUP BY th.[Date], th.[Store No_]
ORDER BY th.[Date];
