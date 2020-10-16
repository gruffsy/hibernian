set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off

select 
	prodno as 'Produktnummer',
	trinf1 as 'Lev.prono',
	eanitmNo as 'Strekkode',
	descr as 'Beskrivelse',
	inf as 'Sortimentskode',

( SELECT 
      sum(bal + stcinc - shprsv - shprsvin)
FROM [F0001].[dbo].[StcBal] as ski
where stcno = 1 and ski.prodno = p.prodno
) as 'Skien'
,( SELECT 
      sum(bal + stcinc - shprsv - shprsvin)
FROM [F0001].[dbo].[StcBal] as por
where stcno = 2 and por.prodno = p.prodno
) as 'Porsgrunn'
,( SELECT 
      sum(bal + stcinc - shprsv - shprsvin)
FROM [F0002].[dbo].[StcBal] as kris
where stcno = 1 and kris.prodno = p.prodno
) as 'Kristiansand'
,( SELECT 
      sum(bal + stcinc - shprsv - shprsvin)
FROM [F0003].[dbo].[StcBal] as ton
where stcno = 1 and ton.prodno = p.prodno
) as 'Tonsberg'
,
( SELECT 
      sum(bal + stcinc - shprsv - shprsvin)
FROM [F0004].[dbo].[StcBal] as are
where stcno = 1 and are.prodno = p.prodno
) as 'Arendal'
,
( SELECT 
      sum(bal + stcinc - shprsv - shprsvin)
FROM [F0010].[dbo].[StcBal] as san
where stcno = 1 and san.prodno = p.prodno
) as 'Sandefjord'
,
( SELECT 
      sum(bal + stcinc - shprsv - shprsvin)
FROM [F0016].[dbo].[StcBal] as lar
where stcno = 1 and lar.prodno = p.prodno
) as 'Larvik',
( SELECT 
      sum(bal + stcinc - shprsv - shprsvin)
FROM [F0015].[dbo].[StcBal] as stock
where stcno = 1 and stock.prodno = p.prodno
) as 'Stock'
from [F0001].[dbo].[prod] as p
where prodpro <> 4
go
    quit