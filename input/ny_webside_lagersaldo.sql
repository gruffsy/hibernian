set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off


USE F0001;
SELECT  
	CONVERT(varchar(13), p.EANItmNo) as SkuNumber,
	CONVERT(decimal(25,4), l.Bal + l.StcInc - l.ShpRsv - l.ShpRsvIn) as Quantity,
	CONVERT(varchar(4), 'S140') as Warehouse 
FROM
	StcBal as l,
	Prod as p
WHERE
	l.StcNo = 1 AND
	l.ProdNo = p.ProdNo AND
	p.EANItmNo <> '' AND
	(
	l.prodno = '314128' OR 
	l.prodno = 'GB7199H8BN160' OR
	l.prodno = 'LS3547-OAK'
	)
FOR JSON AUTO;
go
    quit