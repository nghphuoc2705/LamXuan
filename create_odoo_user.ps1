# Script tao user PostgreSQL odoo
# Nhap password cua user postgres khi duoc yeu cau

$pgBin = "C:\Program Files\PostgreSQL\17\bin\psql.exe"
$sqlFile = "create_odoo_user.sql"

Write-Host "Dang tao user PostgreSQL 'odoo' voi password 'odoo' va quyen CREATEDB..." -ForegroundColor Yellow
Write-Host "Vui long nhap password cua user 'postgres' khi duoc yeu cau." -ForegroundColor Cyan

& $pgBin -U postgres -f $sqlFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[OK] User 'odoo' da duoc tao thanh cong!" -ForegroundColor Green
    Write-Host "  - Username: odoo" -ForegroundColor Green
    Write-Host "  - Password: odoo" -ForegroundColor Green
    Write-Host "  - Quyen: CREATEDB" -ForegroundColor Green
} else {
    Write-Host "`n[ERROR] Co loi xay ra. Vui long kiem tra lai." -ForegroundColor Red
}
