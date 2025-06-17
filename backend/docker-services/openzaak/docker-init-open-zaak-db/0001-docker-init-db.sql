CREATE USER openzaak;
CREATE DATABASE openzaak;
ALTER USER openzaak WITH superuser;
-- On Postgres 15+, connect to the database and grant schema permissions.
-- GRANT USAGE, CREATE ON SCHEMA public TO openzaak;