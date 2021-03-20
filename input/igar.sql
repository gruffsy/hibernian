set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off

	
select
	s.Name as 'butikk',
s.ERPHostCompanyNo,
	s.WarehouseNo,
	FORMAT(sum(tl.extendedprice),'### ### ##0 kr') AS 'mmoms',
	FORMAT(sum((tl.extendedprice) / 1.25),'### ### ##0 kr') AS 'umoms',
	-- FORMAT(sum(((tl.extendedprice) / 1.25) - (tl.costprice * tl.quantity)),'### ### ##0 kr') AS 'db',
	-- FORMAT(sum(((tl.extendedprice) / 1.25) - (tl.costprice * tl.quantity))/sum(tl.extendedprice / 1.25), 'P') as 'dg',
	FORMAT(count(distinct tr.PosTransactionNo), '### ### ##0') as 'antord',
	FORMAT(sum(tl.extendedprice)/count(distinct tr.PosTransactionNo), '### ### ##0 kr') as 'prord'
	
from
	ErpPosDb.dbo.vcrPosTransactionLine tl,
	ErpPosDb.dbo.vcrPosTransaction tr,
	ErpPosDb.dbo.vcrStore s
where
	s.StoreNo = tr.StoreNo and 
	tl.PosTransactionNo = tr.PosTransactionNo 
	and cast(tr.CompletedDate as DATE) = cast(GETDATE()-1 as DATE)
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
	FORMAT(sum(tl.extendedprice),'### ### ##0 kr') AS 'mmoms',
	FORMAT(sum((tl.extendedprice) / 1.25),'### ### ##0 kr') AS 'umoms',
	-- FORMAT(sum(((tl.extendedprice) / 1.25) - (tl.costprice * tl.quantity)),'### ### ##0 kr') AS 'db',
	-- FORMAT(sum(((tl.extendedprice) / 1.25) - (tl.costprice * tl.quantity))/sum(tl.extendedprice / 1.25), 'P') as 'dg',
	FORMAT(count(distinct tr.PosTransactionNo), '### ### ##0') as 'antord',
	FORMAT(sum(tl.extendedprice)/count(distinct tr.PosTransactionNo), '### ### ##0 kr') as 'prord'
	
from
	ErpPosDb.dbo.vcrPosTransactionLine tl,
	ErpPosDb.dbo.vcrPosTransaction tr,
	ErpPosDb.dbo.vcrStore s
where
	s.StoreNo = tr.StoreNo and 
	tl.PosTransactionNo = tr.PosTransactionNo 
	and cast(tr.CompletedDate as DATE) = cast(GETDATE()-1 as DATE)
	and tr.Status = 4

	
order by
	
	s.ERPHostCompanyNo,
	s.WarehouseNo,
	s.Name
	
	
	
for json auto
