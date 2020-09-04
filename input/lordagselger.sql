set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off

select top (10) selger,
FORMAT(totalt,'### ### ##0 kr') AS 'Beløp',
butikk
from f0004.dbo.SALG_PR_SELGER
where datepart(weekday, dato) = 7
order by dato desc, totalt desc
for json path
go
    quit
