CREATE TABLE columns_db (
                                        rsid TEXT PRIMARY KEY,
                                        gene TEXT,
                                        chr TEXT NOT NULL,
                                        position INTEGER NOT NULL,
                                        orientation TEXT NOT NULL,
                                        reference TEXT
                                    );
CREATE TABLE genotypes_db (
                                            id integer PRIMARY KEY AUTOINCREMENT,
                                            rsid TEXT,
                                            genotype TEXT NOT NULL,
                                            magnitude REAL,
                                            color TEXT,
                                            summary TEXT
                                        );
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE processed_snps_db (
                rsid TEXT PRIMARY KEY,
                status TEXT NOT NULL
            );
CREATE TABLE not_found_snps_db (
                rsid TEXT PRIMARY KEY,
                status TEXT
            );
