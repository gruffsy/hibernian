set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian;
set
    noexec off

SELECT
    Item.No_ AS Nr,
    Item.GTIN AS EAN,
    Item.[Vendor Item No_] AS [Lev. varenr],
    Item.Description AS Beskrivelse,
    Item.[Unit Cost] AS Kostpris,
    (Item.[Unit Price] - Item.[Unit Cost]) / Item.[Unit Price] AS [Dg. %],
    Item.[Indirect Cost _] AS [Indirekte kost],
    Item.[Unit Price Including VAT] AS Normalpris,
    Item.[Sales Unit of Measure] AS Basisenhet,
    ItemCategory.Code AS Hovedgruppenr,
    ItemCategory.Description AS Hovedgruppe,
    ProductGroup.Code AS Varegruppenr,
    ProductGroup.Description AS Varegruppe,
    Vendor.No_ AS [Leverandør nr],
    Vendor.Name AS Leverandør,
    Item.[Attrib 2 Code] AS Sortimentkode,
    Item.[Order Multiple] AS [Kolli str],
    Item.[Web Item] AS [På nett],
    Item.[Date Created] AS [Opprettet dato],
    Item.[Last Date Modified] AS [Endret dato],
    [MegaFlisMASTER$Item Family].Code AS BrandID,
    [MegaFlisMASTER$Item Family].Description AS Brand
FROM
    MegaFlisMASTER$Item AS Item 
    INNER JOIN
    [MegaFlisMASTER$Item Category] AS ItemCategory 
    ON ItemCategory.Code = Item.[Item Category Code] 
    INNER JOIN
    [MegaFlisMASTER$Product Group] AS ProductGroup ON ProductGroup.Code = Item.[Product Group Code] 
    AND ItemCategory.Code = ProductGroup.[Item Category Code] 
    INNER JOIN
    MegaFlisMASTER$Vendor AS Vendor ON Vendor.No_ = Item.[Vendor No_] 
    LEFT OUTER JOIN
    [MegaFlisMASTER$Item Family] ON Item.[Item Family Code] = [MegaFlisMASTER$Item Family].Code
WHERE
    (Item.[Unit Price] > 0)

go
quit

