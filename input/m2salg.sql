set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off

	
select
	tl.ProductNo,
	tl.ProductName,
	sum(tl.quantity)
	
from
	ErpPosDb.dbo.vcrPosTransactionLine tl,
	ErpPosDb.dbo.vcrPosTransaction tr,
	ErpPosDb.dbo.vcrStore s
where
	s.StoreNo = tr.StoreNo and 
	tl.PosTransactionNo = tr.PosTransactionNo 
	and cast(tr.CompletedDate as DATE) > '2020-01-01'
	and tr.Status = 4
	and tl.UnitNo = 2
	
	group by
	tl.ProductNo,
	tl.ProductName
	order by 
	tl.ProductNo
