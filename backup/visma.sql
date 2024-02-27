set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off

	
select 
    butikk,
    Klient,
    sum(m_mva) AS 'mmoms',
    sum(u_mva) AS 'umoms',
    sum(u_mva - kostnad) AS 'db',
    sum(u_mva - kostnad)/sum(u_mva) as 'dg',
    count(distinct Ordrenummer) as 'antord',
    sum(m_mva)/count(distinct Ordrenummer) as 'prord'
from 
    f0001.dbo.PRODUKTRANSER_ALLE
where 
    fakturadato = convert(varchar, getdate(), 112)
    and Fakturadato <> 0
    and transaksjonstype = 1
    and Ordretype = 3


group by
    butikk,
    Klient

order by
    Klient
	
for json path
