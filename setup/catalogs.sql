-- Catalogs je Umgebung. Free Edition: Bundle kann keine Catalogs anlegen (Default Storage), siehe ADR 0004.

CREATE CATALOG IF NOT EXISTS redbricks_dev
COMMENT 'redbricks Lakehouse: alle Daten der Umgebung dev (Landing Zone, Betrieb, Data Products)';

CREATE CATALOG IF NOT EXISTS redbricks_test
COMMENT 'redbricks Lakehouse: alle Daten der Umgebung test (Landing Zone, Betrieb, Data Products)';

CREATE CATALOG IF NOT EXISTS redbricks_prod
COMMENT 'redbricks Lakehouse: alle Daten der Umgebung prod (Landing Zone, Betrieb, Data Products)';