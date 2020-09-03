set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off

select
	'Totalt' As Totalt,
	FORMAT(sum(tl.extendedprice),'### ### ##0 kr') AS 'Beløp m/mva',
	FORMAT(sum((tl.extendedprice) / 1.25),'### ### ##0 kr') AS 'Beløp u/mva',
	FORMAT(sum(((tl.extendedprice) / 1.25) - (tl.costprice * tl.quantity)),'### ### ##0 kr') AS 'DB',
	FORMAT(sum(((tl.extendedprice) / 1.25) - (tl.costprice * tl.quantity))/sum(tl.extendedprice / 1.25), 'P') as 'DG',
	FORMAT(count(distinct tr.PosTransactionNo), '### ### ##0') as 'Antall ordre',
	FORMAT(sum(tl.extendedprice)/count(distinct tr.PosTransactionNo), '### ### ##0 kr') as 'per kunde'
	
from
	ErpPosDb.dbo.vcrPosTransactionLine tl,
	ErpPosDb.dbo.vcrPosTransaction tr,
	ErpPosDb.dbo.vcrStore s
where
	s.StoreNo = tr.StoreNo and 
	tl.PosTransactionNo = tr.PosTransactionNo 
	and cast(tr.CompletedDate as DATE) = cast(GETDATE() as DATE)
	and tr.Status = 4
	
for json auto

