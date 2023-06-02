--
-- PostgreSQL database dump
--

-- Dumped from database version 15.0
-- Dumped by pg_dump version 15.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: files; Type: TABLE; Schema: public; Owner: olivia
--

CREATE TABLE public.files (
    file_id integer NOT NULL,
    user_id integer,
    filename text,
    file_date date,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.files OWNER TO olivia;

--
-- Name: files_file_id_seq; Type: SEQUENCE; Schema: public; Owner: olivia
--

CREATE SEQUENCE public.files_file_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.files_file_id_seq OWNER TO olivia;

--
-- Name: files_file_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: olivia
--

ALTER SEQUENCE public.files_file_id_seq OWNED BY public.files.file_id;


--
-- Name: observedphenotypes; Type: TABLE; Schema: public; Owner: olivia
--

CREATE TABLE public.observedphenotypes (
    observed_phenotype_id integer NOT NULL,
    user_id integer,
    characteristic text,
    variation text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.observedphenotypes OWNER TO olivia;

--
-- Name: observedphenotypes_observed_phenotype_id_seq; Type: SEQUENCE; Schema: public; Owner: olivia
--

CREATE SEQUENCE public.observedphenotypes_observed_phenotype_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.observedphenotypes_observed_phenotype_id_seq OWNER TO olivia;

--
-- Name: observedphenotypes_observed_phenotype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: olivia
--

ALTER SEQUENCE public.observedphenotypes_observed_phenotype_id_seq OWNED BY public.observedphenotypes.observed_phenotype_id;


--
-- Name: processed_snps; Type: TABLE; Schema: public; Owner: olivia
--

CREATE TABLE public.processed_snps (
    rs_id text NOT NULL,
    snpedia_processed boolean DEFAULT false
);


ALTER TABLE public.processed_snps OWNER TO olivia;

--
-- Name: snpediametadata; Type: TABLE; Schema: public; Owner: olivia
--

CREATE TABLE public.snpediametadata (
    rs_id text NOT NULL,
    gene text,
    "position" integer,
    orientation text,
    reference text,
    magnitude real,
    color text,
    summary text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    chromosome text,
    genotype text NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.snpediametadata OWNER TO olivia;

--
-- Name: snpediametadata_id_seq; Type: SEQUENCE; Schema: public; Owner: olivia
--

CREATE SEQUENCE public.snpediametadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.snpediametadata_id_seq OWNER TO olivia;

--
-- Name: snpediametadata_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: olivia
--

ALTER SEQUENCE public.snpediametadata_id_seq OWNED BY public.snpediametadata.id;


--
-- Name: snps; Type: TABLE; Schema: public; Owner: olivia
--

CREATE TABLE public.snps (
    rs_id text NOT NULL,
    chromosome_number text,
    "position" integer,
    reference text,
    alternate text,
    qual text,
    filter text,
    info text,
    format text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.snps OWNER TO olivia;

--
-- Name: users; Type: TABLE; Schema: public; Owner: olivia
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    nickname text,
    source text DEFAULT 'GenomePrep_19.02.2020'::text,
    sequencing_service text,
    sequencing_date date,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO olivia;

--
-- Name: usersnps; Type: TABLE; Schema: public; Owner: olivia
--

CREATE TABLE public.usersnps (
    user_snp_id integer NOT NULL,
    user_id integer,
    file_id integer,
    rs_id text,
    genotype text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.usersnps OWNER TO olivia;

--
-- Name: usersnps_user_snp_id_seq; Type: SEQUENCE; Schema: public; Owner: olivia
--

CREATE SEQUENCE public.usersnps_user_snp_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.usersnps_user_snp_id_seq OWNER TO olivia;

--
-- Name: usersnps_user_snp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: olivia
--

ALTER SEQUENCE public.usersnps_user_snp_id_seq OWNED BY public.usersnps.user_snp_id;


--
-- Name: files file_id; Type: DEFAULT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.files ALTER COLUMN file_id SET DEFAULT nextval('public.files_file_id_seq'::regclass);


--
-- Name: observedphenotypes observed_phenotype_id; Type: DEFAULT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.observedphenotypes ALTER COLUMN observed_phenotype_id SET DEFAULT nextval('public.observedphenotypes_observed_phenotype_id_seq'::regclass);


--
-- Name: snpediametadata id; Type: DEFAULT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.snpediametadata ALTER COLUMN id SET DEFAULT nextval('public.snpediametadata_id_seq'::regclass);


--
-- Name: usersnps user_snp_id; Type: DEFAULT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.usersnps ALTER COLUMN user_snp_id SET DEFAULT nextval('public.usersnps_user_snp_id_seq'::regclass);


--
-- Name: files filename_unique; Type: CONSTRAINT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT filename_unique UNIQUE (filename);


--
-- Name: files files_pkey; Type: CONSTRAINT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_pkey PRIMARY KEY (file_id);


--
-- Name: observedphenotypes observedphenotypes_pkey; Type: CONSTRAINT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.observedphenotypes
    ADD CONSTRAINT observedphenotypes_pkey PRIMARY KEY (observed_phenotype_id);


--
-- Name: processed_snps processed_snps_pkey; Type: CONSTRAINT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.processed_snps
    ADD CONSTRAINT processed_snps_pkey PRIMARY KEY (rs_id);


--
-- Name: snpediametadata snpediametadata_pkey; Type: CONSTRAINT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.snpediametadata
    ADD CONSTRAINT snpediametadata_pkey PRIMARY KEY (id);


--
-- Name: snpediametadata snpediametadata_unique; Type: CONSTRAINT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.snpediametadata
    ADD CONSTRAINT snpediametadata_unique UNIQUE (rs_id, gene, "position", orientation, reference, magnitude, color, summary, chromosome, genotype, id);


--
-- Name: snps snps_pkey; Type: CONSTRAINT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.snps
    ADD CONSTRAINT snps_pkey PRIMARY KEY (rs_id);


--
-- Name: snps snps_rs_id_key; Type: CONSTRAINT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.snps
    ADD CONSTRAINT snps_rs_id_key UNIQUE (rs_id);


--
-- Name: users user_id_unique; Type: CONSTRAINT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT user_id_unique UNIQUE (user_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: usersnps usersnps_pkey; Type: CONSTRAINT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.usersnps
    ADD CONSTRAINT usersnps_pkey PRIMARY KEY (user_snp_id);


--
-- Name: usersnps usersnps_user_file_rs_id_key; Type: CONSTRAINT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.usersnps
    ADD CONSTRAINT usersnps_user_file_rs_id_key UNIQUE (user_id, file_id, rs_id);


--
-- Name: idx_snpedia_metadata_rs_id; Type: INDEX; Schema: public; Owner: olivia
--

CREATE INDEX idx_snpedia_metadata_rs_id ON public.snpediametadata USING btree (rs_id);


--
-- Name: idx_snps_rs_id; Type: INDEX; Schema: public; Owner: olivia
--

CREATE INDEX idx_snps_rs_id ON public.snps USING btree (rs_id);


--
-- Name: files files_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: observedphenotypes observedphenotypes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.observedphenotypes
    ADD CONSTRAINT observedphenotypes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: snpediametadata snpediametadata_rs_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.snpediametadata
    ADD CONSTRAINT snpediametadata_rs_id_fkey FOREIGN KEY (rs_id) REFERENCES public.snps(rs_id);


--
-- Name: usersnps usersnps_file_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.usersnps
    ADD CONSTRAINT usersnps_file_id_fkey FOREIGN KEY (file_id) REFERENCES public.files(file_id);


--
-- Name: usersnps usersnps_rs_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.usersnps
    ADD CONSTRAINT usersnps_rs_id_fkey FOREIGN KEY (rs_id) REFERENCES public.snps(rs_id);


--
-- Name: usersnps usersnps_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: olivia
--

ALTER TABLE ONLY public.usersnps
    ADD CONSTRAINT usersnps_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO olivia;


--
-- PostgreSQL database dump complete
--

