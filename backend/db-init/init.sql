-- backend/db-init/init.sql
CREATE TABLE IF NOT EXISTS files (
    id UUID PRIMARY KEY,
    filename TEXT NOT NULL,
    checksum TEXT NOT NULL,
    status TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

-- Sätt defaults
INSERT INTO settings (key, value) VALUES
('rbac_enabled', 'false'),
('oidc_enabled', 'false')
ON CONFLICT (key) DO NOTHING;
