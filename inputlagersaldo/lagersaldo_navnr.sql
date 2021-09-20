set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off

SELECT p.trinf3 as 'No_'
      , '140' as 'Location' 
	  ,sum(bal + stcinc) AS 'Inventory'
	  ,sum((bal+stcinc)-(shprsv+shprsvin)) as 'Saleable qty'
      FROM [F0001].[dbo].[StcBal] s, [F0001].[dbo].[prod] p
	  where
	  s.prodno = p.ProdNo
	  AND
	  StcNo = 1
	  AND
	  p.trinf3 <> ''
	  group by
	  p.TrInf3
UNION ALL
SELECT p.trinf3 as 'No_'
      , '110' as 'Location' 
	  ,sum(bal + stcinc) AS 'Inventory'
	  ,sum((bal+stcinc)-(shprsv+shprsvin)) as 'Saleable qty'
      FROM [F0004].[dbo].[StcBal] s, [F0001].[dbo].[prod] p
	  where
	  s.prodno = p.ProdNo
	  AND
	  StcNo = 1
	  AND
	  p.trinf3 <> ''
	  group by
	  p.TrInf3
UNION ALL
SELECT p.trinf3 as 'No_'
      , '120' as 'Location' 
	  ,sum(bal + stcinc) AS 'Inventory'
	  ,sum((bal+stcinc)-(shprsv+shprsvin)) as 'Saleable qty'
      FROM [F0001].[dbo].[StcBal] s, [F0001].[dbo].[prod] p
	  where
	  s.prodno = p.ProdNo
	  AND
	  StcNo = 2
	  AND
	  p.trinf3 <> ''
	  group by
	  p.TrInf3

UNION ALL
SELECT p.trinf3 as 'No_'
      , '130' as 'Location' 
	  ,sum(bal + stcinc) AS 'Inventory'
	  ,sum((bal+stcinc)-(shprsv+shprsvin)) as 'Saleable qty'
      FROM [F0010].[dbo].[StcBal] s, [F0001].[dbo].[prod] p
	  where
	  s.prodno = p.ProdNo
	  AND
	  StcNo = 1
	  AND
	  p.trinf3 <> ''
	  group by
	  p.TrInf3

UNION ALL
SELECT p.trinf3 as 'No_'
      , '150' as 'Location' 
	  ,sum(bal + stcinc) AS 'Inventory'
	  ,sum((bal+stcinc)-(shprsv+shprsvin)) as 'Saleable qty'
      FROM [F0002].[dbo].[StcBal] s, [F0001].[dbo].[prod] p
	  where
	  s.prodno = p.ProdNo
	  AND
	  StcNo = 1
	  AND
	  p.trinf3 <> ''
	  group by
	  p.TrInf3

UNION ALL
SELECT p.trinf3 as 'No_'
      , '160' as 'Location' 
	  ,sum(bal + stcinc) AS 'Inventory'
	  ,sum((bal+stcinc)-(shprsv+shprsvin)) as 'Saleable qty'
      FROM [F0003].[dbo].[StcBal] s, [F0001].[dbo].[prod] p
	  where
	  s.prodno = p.ProdNo
	  AND
	  StcNo = 1
	  AND
	  p.trinf3 <> ''
	  group by
	  p.TrInf3

UNION ALL
SELECT p.trinf3 as 'No_'
      , '170' as 'Location' 
	  ,sum(bal + stcinc) AS 'Inventory'
	  ,sum((bal+stcinc)-(shprsv+shprsvin)) as 'Saleable qty'
      FROM [F0016].[dbo].[StcBal] s, [F0001].[dbo].[prod] p
	  where
	  s.prodno = p.ProdNo
	  AND
	  StcNo = 1
	  AND
	  p.trinf3 <> ''
	  group by
	  p.TrInf3
go
    quit