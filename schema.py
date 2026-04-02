DATABASE_SCHEMA= """
=== BATABASE SCHEMA ===
CREATE TABLE IF NOT EXISTS "produk"(
  "id"  INTEGER,
  "nama"        TEXT NOT NULL,
  "harga"       INTEGER NOT NULL,
  "stok"        INTEGER NOT NULL,
  PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE IF NOT EXISTS "pembeli"(
  "id"  INTEGER NOT NULL,
  "nama"        TEXT NOT NULL,
  "umur"        INTEGER NOT NULL,
  PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "transaksi"(
  "id"  INTEGER NOT NULL,
  "id_pembeli"  INTEGER NOT NULL,
  "id_produk"   INTEGER NOT NULL,
  PRIMARY KEY("id"),
  FOREIGN KEY("id_pembeli") REFERENCES "pembeli"("id") ON DELETE CASCADE,
  FOREIGN KEY("id_produk") REFERENCES "produk"("id") ON DELETE CASCADE
);
"""