set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off
select (
SELECT 
	p.ProdNo as 'Prodno'
	,p.descr as 'Beskrivelse'
    ,CAST(sum(s.bal + s.stcinc - ino + cino) as decimal(7,1)) as 'm2 på lager'
	,CAST(p.Free1 AS DECIMAL(7,1)) as 'm2 pr pall'
	,CAST((sum(s.bal + s.stcinc - ino + cino)/NULLIF(p.free1, 0)) as DECIMAL(7,0)) as  'Paller på lager'
    ,CAST(sum(s.InPurc/NULLIF(p.free1, 0)) as DECIMAL(7,0)) as 'Paller på vei'
  FROM F0015.dbo.StcBal s, f0015.dbo.prod p
  where 
  s.prodno = p.prodno
  and p.ProdPrGr <> 99
  and s.StcNo = 1
  and s.prodno <> 'adm'

  group by
  p.ProdNo
	,p.descr
	,p.Free1
   
	order by p.Descr, p.ProdNo
	for json auto
)