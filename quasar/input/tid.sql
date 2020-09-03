set
    nocount on
set
    noexec on
SET
    LANGUAGE Norwegian
set
    noexec off

SELECT FORMAT (getdate(), 'dddd MMMM yyyy - HH:mm') as "Oppdatert"
for json path
