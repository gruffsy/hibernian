set
    nocount on
set
    noexec on

set
    noexec off

SELECT FORMAT (getdate(), 'HH:mm - dddd dd. MMMM yyyy', 'no-NO') as "oppdatert"
for json path;



