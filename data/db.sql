CREATE TABLE users (
    user_id INT PRIMARY KEY,
    nickname TEXT,
    source TEXT DEFAULT 'GenomePrep_19.02.2020',
    sequencing_service TEXT,
    sequencing_date DATE DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE files (
    file_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    filename TEXT,
    file_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE snps (
    rs_id TEXT PRIMARY KEY,
    chromosome_number INT,
    position INT,
    reference TEXT,
    alternate TEXT,
    qual TEXT,
    filter TEXT,
    info TEXT,
    format TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_snps_rs_id ON snps (rs_id);

CREATE TABLE usersnps (
    user_snp_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    file_id INT REFERENCES files(file_id),
    rs_id TEXT REFERENCES snps(rs_id),
    genotype TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE observedphenotypes (
    observed_phenotype_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    characteristic TEXT,
    variation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE snpediametadata (
    rs_id TEXT PRIMARY KEY REFERENCES snps(rs_id),
    gene TEXT,
    position INT,
    orientation TEXT,
    reference TEXT,
    magnitude REAL,
    color TEXT,
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_snpedia_metadata_rs_id ON snpediametadata (rs_id);
