set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off

SELECT 
	s.ProdNo as Prodno
	,p.descr as Beskrivelse
    ,CAST(s.bal + s.stcinc - ino + cino as decimal(7,1)) as 'm2'
	,CAST(p.Free1 AS DECIMAL(7,1)) as 'Prpall'
	,CAST((s.bal + s.stcinc - ino + cino)/NULLIF(p.free1, 0) as DECIMAL(7,0)) as  'Paller'
  FROM F0015.dbo.StcBal s, f0015.dbo.prod p
  where 
  s.prodno = p.prodno
  and p.ProdPrGr <> 99
  and s.StcNo = 1
  and s.prodno <> 'adm'
  
	order by p.Descr
	for json path