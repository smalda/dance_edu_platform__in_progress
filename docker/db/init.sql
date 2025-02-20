DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'smalda') THEN

      CREATE ROLE smalda WITH LOGIN PASSWORD '1234';
   END IF;
END
$do$;

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE dance_edu OWNER smalda'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'dance_edu')\gexec
