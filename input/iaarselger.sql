set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off

select top 10 selger,
FORMAT(sum(totalt),'### ### ##0 kr') AS 'Beløp',

butikk as 'butikk'
from f0004.dbo.SALG_PR_SELGER
where datepart(year, dato) = datepart(year, cast(getdate() as Date))

group by
selger,
butikk
order by sum(totalt) desc
for json path
go
    quit
