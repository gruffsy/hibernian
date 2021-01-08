
	
SELECT 
m1.butikk as 'butikk',
 
FORMAT(m1.mmoms - m2.mmoms,'### ### ##0 kr') AS 'mmoms',
	FORMAT(m1.umoms - m2.umoms ,'### ### ##0 kr') AS 'umoms',
	FORMAT(m1.db - m2.db,'### ### ##0 kr') AS 'db',
	FORMAT(m1.dg - m2.dg, 'P') as 'dg',
	FORMAT(m1.antord - m2.antord, '### ### ##0') as 'antord',
	FORMAT(m1.prord - m2.prord, '### ### ##0 kr') as 'prord'

from
(






select
	s.Name as 'butikk',
s.ERPHostCompanyNo,
	s.WarehouseNo,
	sum(tl.extendedprice) AS 'mmoms',
	sum((tl.extendedprice) / 1.25) AS 'umoms',
	sum(((tl.extendedprice) / 1.25) - (tl.costprice * tl.quantity)) AS 'db',
	sum(((tl.extendedprice) / 1.25) - (tl.costprice * tl.quantity))/sum(tl.extendedprice / 1.25) as 'dg',
	count(distinct tr.PosTransactionNo) as 'antord',
	sum(tl.extendedprice)/count(distinct tr.PosTransactionNo) as 'prord'
	
from
	ErpPosDb.dbo.vcrPosTransactionLine tl,
	ErpPosDb.dbo.vcrPosTransaction tr,
	ErpPosDb.dbo.vcrStore s
where
	s.StoreNo = tr.StoreNo and 
	tl.PosTransactionNo = tr.PosTransactionNo 
	and CAST(tr.CompletedDate as DATE) <= DATEADD(YEAR, -1, CAST(GETDATE() as DATE))
	and format(cast(tr.CompletedDate as DATE), 'yyyy') = format(DATEADD(YEAR, -1, CAST(GETDATE() as DATE)), 'yyyy')
	and tr.Status = 4
	
	group by
	
	s.ERPHostCompanyNo,
	s.WarehouseNo,
	s.Name

union all
select
	'Totalt' As 'butikk',
9999,
9999,
	sum(tl.extendedprice) AS 'mmoms',
	sum((tl.extendedprice) / 1.25) AS 'umoms',
	sum(((tl.extendedprice) / 1.25) - (tl.costprice * tl.quantity)) AS 'db',
	sum(((tl.extendedprice) / 1.25) - (tl.costprice * tl.quantity))/sum(tl.extendedprice / 1.25) as 'dg',
	count(distinct tr.PosTransactionNo) as 'antord',
	sum(tl.extendedprice)/count(distinct tr.PosTransactionNo) as 'prord'
	
from
	ErpPosDb.dbo.vcrPosTransactionLine tl,
	ErpPosDb.dbo.vcrPosTransaction tr,
	ErpPosDb.dbo.vcrStore s
where
	s.StoreNo = tr.StoreNo and 
	tl.PosTransactionNo = tr.PosTransactionNo 
	and CAST(tr.CompletedDate as DATE) <= DATEADD(YEAR, -1, CAST(GETDATE() as DATE))
	and format(cast(tr.CompletedDate as DATE), 'yyyy') = format(DATEADD(YEAR, -1, CAST(GETDATE() as DATE)), 'yyyy')
	and tr.Status = 4

	

	) as m2
	cross join

	(

	select
	s.Name as 'butikk',
s.ERPHostCompanyNo,
	s.WarehouseNo,
	sum(tl.extendedprice) AS 'mmoms',
	sum((tl.extendedprice) / 1.25) AS 'umoms',
	sum(((tl.extendedprice) / 1.25) - (tl.costprice * tl.quantity)) AS 'db',
	sum(((tl.extendedprice) / 1.25) - (tl.costprice * tl.quantity))/sum(tl.extendedprice / 1.25) as 'dg',
	count(distinct tr.PosTransactionNo) as 'antord',
	sum(tl.extendedprice)/count(distinct tr.PosTransactionNo) as 'prord'
	
from
	ErpPosDb.dbo.vcrPosTransactionLine tl,
	ErpPosDb.dbo.vcrPosTransaction tr,
	ErpPosDb.dbo.vcrStore s
where
	s.StoreNo = tr.StoreNo and 
	tl.PosTransactionNo = tr.PosTransactionNo 
	and format(cast(tr.CompletedDate as DATE), 'yyyy') = format(cast(GETDATE() as DATE), 'yyyy')
	and tr.Status = 4
	
	group by
	
	s.ERPHostCompanyNo,
	s.WarehouseNo,
	s.Name

union all
select
	'Totalt' As 'butikk',
9999,
9999,
	sum(tl.extendedprice) AS 'mmoms',
	sum((tl.extendedprice) / 1.25) AS 'umoms',
	sum(((tl.extendedprice) / 1.25) - (tl.costprice * tl.quantity)) AS 'db',
	sum(((tl.extendedprice) / 1.25) - (tl.costprice * tl.quantity))/sum(tl.extendedprice / 1.25) as 'dg',
	count(distinct tr.PosTransactionNo) as 'antord',
	sum(tl.extendedprice)/count(distinct tr.PosTransactionNo) as 'prord'
	
from
	ErpPosDb.dbo.vcrPosTransactionLine tl,
	ErpPosDb.dbo.vcrPosTransaction tr,
	ErpPosDb.dbo.vcrStore s
where
	s.StoreNo = tr.StoreNo and 
	tl.PosTransactionNo = tr.PosTransactionNo 
	and format(cast(tr.CompletedDate as DATE), 'yyyy') = format(cast(GETDATE() as DATE), 'yyyy')
	and tr.Status = 4

	

	
	) as m1

	where m1.butikk = m2.butikk
	order by
	m1.ERPHostCompanyNo, m1.WarehouseNo

for json auto