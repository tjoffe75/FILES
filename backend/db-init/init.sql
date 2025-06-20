-- backend/db-init/init.sql
CREATE TABLE IF NOT EXISTS files (
    id UUID PRIMARY KEY,
    filename TEXT NOT NULL,
    checksum TEXT NOT NULL,
    status TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
