DECLARE @window_start_date date = ?;

SET DATEFIRST 1;

WITH Sales AS (
    SELECT
        SalesEntry.[Date] AS Dato,
        SalesEntry.[Sales Staff] AS Selger,
        CASE DATEPART(WEEKDAY, SalesEntry.[Date])
            WHEN 1 THEN 'Mandag'
            WHEN 2 THEN 'Tirsdag'
            WHEN 3 THEN 'Onsdag'
            WHEN 4 THEN 'Torsdag'
            WHEN 5 THEN 'Fredag'
            WHEN 6 THEN 'Lørdag'
            WHEN 7 THEN 'Søndag'
        END AS ukedag,
        -(SUM(SalesEntry.[Net Amount])) AS umoms,
        -(SUM(SalesEntry.[Net Amount]) - SUM(SalesEntry.[Cost Amount])) AS db,
        Staff.[First Name] AS Fornavn,
        Staff.[Last Name] AS Etternavn,
        Staff.[Store No_] AS ButikkID
    FROM [Hibernian Retail$LSC Staff$5ecfc871-5d82-43f1-9c54-59685e82318d] Staff,
         [Megaflis_AS].[dbo].[mf_trans_sales_entry__hib] SalesEntry
    INNER JOIN [mf_transaction_header__hib] th
        ON th.[Store No_] = SalesEntry.[Store No_]
       AND th.[POS Terminal No_] = SalesEntry.[POS Terminal No_]
       AND th.[Transaction No_] = SalesEntry.[Transaction No_]
    LEFT JOIN [Hibernian Retail$Customer$437dbf0e-84ff-417a-965d-ed2bb9650972] c
        ON th.[Customer No_] = c.No_
    WHERE th.[Transaction Type] = 2
      AND th.[Entry Status] IN (0, 2)
      AND CAST(th.[Date] AS date) >= @window_start_date
      AND NULLIF(th.[Receipt No_], '') IS NOT NULL
      AND (c.[Customer Price Group] IS NULL OR c.[Customer Price Group] <> 'INTERNT')
      AND SalesEntry.[Sales Staff] = Staff.[Sales Person]
      AND th.[Customer Account] = 0
    GROUP BY
        SalesEntry.[Date],
        SalesEntry.[Sales Staff],
        Staff.[First Name],
        Staff.[Last Name],
        Staff.[Store No_]
    HAVING SalesEntry.[Sales Staff] <> ''
)
SELECT
    ukedag,
    [Fornavn] + ' ' + [Etternavn] AS navn,
    CAST(umoms AS int) AS umoms,
    CAST(db AS int) AS db,
    CASE
        WHEN ButikkID = 'S150' THEN 'Kristiansand'
        WHEN ButikkID = 'S100' THEN 'Bamble'
        WHEN ButikkID = 'S110' THEN 'Arendal'
        WHEN ButikkID = 'S140' THEN 'Skien'
        WHEN ButikkID = 'S130' THEN 'Sandefjord'
        WHEN ButikkID = 'S170' THEN 'Larvik'
        WHEN ButikkID = 'S160' THEN 'Tønsberg'
    END AS butikk,
    CONVERT(INT, CONVERT(VARCHAR, Dato, 112)) AS fakturadato
FROM Sales
ORDER BY Dato DESC, umoms DESC;
