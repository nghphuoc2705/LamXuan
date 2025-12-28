-- Tạo user odoo với password odoo và quyền CREATEDB
-- Nếu user đã tồn tại, sẽ báo lỗi nhưng không sao
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'odoo') THEN
        CREATE USER odoo WITH PASSWORD 'odoo' CREATEDB;
    ELSE
        ALTER USER odoo WITH PASSWORD 'odoo' CREATEDB;
    END IF;
END
$$;

