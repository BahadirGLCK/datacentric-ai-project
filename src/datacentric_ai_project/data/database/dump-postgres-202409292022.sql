--
-- PostgreSQL database cluster dump
--

-- Started on 2024-09-29 20:22:26 +03

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE bahadirgolcuk;
ALTER ROLE bahadirgolcuk WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS;






--
-- Databases
--

--
-- Database "template1" dump
--

\connect template1

--
-- PostgreSQL database dump
--

-- Dumped from database version 14.13 (Homebrew)
-- Dumped by pg_dump version 14.13 (Homebrew)

-- Started on 2024-09-29 20:22:26 +03

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

-- Completed on 2024-09-29 20:22:26 +03

--
-- PostgreSQL database dump complete
--

--
-- Database "postgres" dump
--

\connect postgres

--
-- PostgreSQL database dump
--

-- Dumped from database version 14.13 (Homebrew)
-- Dumped by pg_dump version 14.13 (Homebrew)

-- Started on 2024-09-29 20:22:26 +03

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
-- TOC entry 209 (class 1259 OID 16384)
-- Name: companies; Type: TABLE; Schema: public; Owner: bahadirgolcuk
--

CREATE TABLE public.companies (
    company_id uuid NOT NULL,
    company_name character varying,
    contact_person character varying,
    contact_email character varying
);


ALTER TABLE public.companies OWNER TO bahadirgolcuk;

--
-- TOC entry 3697 (class 0 OID 0)
-- Dependencies: 209
-- Name: TABLE companies; Type: COMMENT; Schema: public; Owner: bahadirgolcuk
--

COMMENT ON TABLE public.companies IS 'Define companies that are using devices';


--
-- TOC entry 215 (class 1259 OID 16456)
-- Name: detections; Type: TABLE; Schema: public; Owner: bahadirgolcuk
--

CREATE TABLE public.detections (
    detection_id uuid NOT NULL,
    image_id uuid,
    label_id uuid,
    confidence_score real,
    bbox_file_url character varying,
    detection_timestamp timestamp with time zone
);


ALTER TABLE public.detections OWNER TO bahadirgolcuk;

--
-- TOC entry 211 (class 1259 OID 16403)
-- Name: device_types; Type: TABLE; Schema: public; Owner: bahadirgolcuk
--

CREATE TABLE public.device_types (
    device_type_id uuid NOT NULL,
    device_type character varying
);


ALTER TABLE public.device_types OWNER TO bahadirgolcuk;

--
-- TOC entry 212 (class 1259 OID 16410)
-- Name: devices; Type: TABLE; Schema: public; Owner: bahadirgolcuk
--

CREATE TABLE public.devices (
    device_id uuid NOT NULL,
    device_type_id uuid,
    factory_id uuid,
    is_test_device boolean,
    is_installed boolean,
    is_data_collector boolean,
    installation_date date
);


ALTER TABLE public.devices OWNER TO bahadirgolcuk;

--
-- TOC entry 210 (class 1259 OID 16391)
-- Name: factories; Type: TABLE; Schema: public; Owner: bahadirgolcuk
--

CREATE TABLE public.factories (
    factory_id uuid NOT NULL,
    company_id uuid NOT NULL,
    factory_name character varying,
    factory_country character varying,
    factory_city character varying
);


ALTER TABLE public.factories OWNER TO bahadirgolcuk;

--
-- TOC entry 213 (class 1259 OID 16425)
-- Name: images; Type: TABLE; Schema: public; Owner: bahadirgolcuk
--

CREATE TABLE public.images (
    image_id uuid NOT NULL,
    device_id uuid,
    image_url character varying,
    capture_timestamp timestamp with time zone,
    is_trainable boolean,
    image_resoulution integer,
    augmentation character varying
);


ALTER TABLE public.images OWNER TO bahadirgolcuk;

--
-- TOC entry 214 (class 1259 OID 16449)
-- Name: labels; Type: TABLE; Schema: public; Owner: bahadirgolcuk
--

CREATE TABLE public.labels (
    label_id uuid NOT NULL,
    label_name character varying
);


ALTER TABLE public.labels OWNER TO bahadirgolcuk;

--
-- TOC entry 216 (class 1259 OID 16473)
-- Name: detection_summary; Type: VIEW; Schema: public; Owner: bahadirgolcuk
--

CREATE VIEW public.detection_summary AS
 SELECT i.image_id,
    i.capture_timestamp,
    l.label_name,
    d.confidence_score,
    f.factory_name,
    dt.device_type,
    i.is_trainable,
    dev.is_data_collector,
    d.bbox_file_url
   FROM (((((public.detections d
     JOIN public.images i ON ((d.image_id = i.image_id)))
     JOIN public.labels l ON ((d.label_id = l.label_id)))
     JOIN public.devices dev ON ((i.device_id = dev.device_id)))
     JOIN public.factories f ON ((dev.factory_id = f.factory_id)))
     JOIN public.device_types dt ON ((dev.device_type_id = dt.device_type_id)));


ALTER TABLE public.detection_summary OWNER TO bahadirgolcuk;

--
-- TOC entry 3685 (class 0 OID 16384)
-- Dependencies: 209
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: bahadirgolcuk
--

COPY public.companies (company_id, company_name, contact_person, contact_email) FROM stdin;
\.


--
-- TOC entry 3691 (class 0 OID 16456)
-- Dependencies: 215
-- Data for Name: detections; Type: TABLE DATA; Schema: public; Owner: bahadirgolcuk
--

COPY public.detections (detection_id, image_id, label_id, confidence_score, bbox_file_url, detection_timestamp) FROM stdin;
\.


--
-- TOC entry 3687 (class 0 OID 16403)
-- Dependencies: 211
-- Data for Name: device_types; Type: TABLE DATA; Schema: public; Owner: bahadirgolcuk
--

COPY public.device_types (device_type_id, device_type) FROM stdin;
\.


--
-- TOC entry 3688 (class 0 OID 16410)
-- Dependencies: 212
-- Data for Name: devices; Type: TABLE DATA; Schema: public; Owner: bahadirgolcuk
--

COPY public.devices (device_id, device_type_id, factory_id, is_test_device, is_installed, is_data_collector, installation_date) FROM stdin;
\.


--
-- TOC entry 3686 (class 0 OID 16391)
-- Dependencies: 210
-- Data for Name: factories; Type: TABLE DATA; Schema: public; Owner: bahadirgolcuk
--

COPY public.factories (factory_id, company_id, factory_name, factory_country, factory_city) FROM stdin;
\.


--
-- TOC entry 3689 (class 0 OID 16425)
-- Dependencies: 213
-- Data for Name: images; Type: TABLE DATA; Schema: public; Owner: bahadirgolcuk
--

COPY public.images (image_id, device_id, image_url, capture_timestamp, is_trainable, image_resoulution, augmentation) FROM stdin;
\.


--
-- TOC entry 3690 (class 0 OID 16449)
-- Dependencies: 214
-- Data for Name: labels; Type: TABLE DATA; Schema: public; Owner: bahadirgolcuk
--

COPY public.labels (label_id, label_name) FROM stdin;
\.


--
-- TOC entry 3526 (class 2606 OID 16390)
-- Name: companies companies_pk; Type: CONSTRAINT; Schema: public; Owner: bahadirgolcuk
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_pk PRIMARY KEY (company_id);


--
-- TOC entry 3538 (class 2606 OID 16462)
-- Name: detections detections_pk; Type: CONSTRAINT; Schema: public; Owner: bahadirgolcuk
--

ALTER TABLE ONLY public.detections
    ADD CONSTRAINT detections_pk PRIMARY KEY (detection_id);


--
-- TOC entry 3530 (class 2606 OID 16409)
-- Name: device_types device_types_pk; Type: CONSTRAINT; Schema: public; Owner: bahadirgolcuk
--

ALTER TABLE ONLY public.device_types
    ADD CONSTRAINT device_types_pk PRIMARY KEY (device_type_id);


--
-- TOC entry 3532 (class 2606 OID 16414)
-- Name: devices devices_pk; Type: CONSTRAINT; Schema: public; Owner: bahadirgolcuk
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_pk PRIMARY KEY (device_id);


--
-- TOC entry 3528 (class 2606 OID 16397)
-- Name: factories factories_pk; Type: CONSTRAINT; Schema: public; Owner: bahadirgolcuk
--

ALTER TABLE ONLY public.factories
    ADD CONSTRAINT factories_pk PRIMARY KEY (factory_id);


--
-- TOC entry 3534 (class 2606 OID 16431)
-- Name: images images_pk; Type: CONSTRAINT; Schema: public; Owner: bahadirgolcuk
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pk PRIMARY KEY (image_id);


--
-- TOC entry 3536 (class 2606 OID 16455)
-- Name: labels labels_pk; Type: CONSTRAINT; Schema: public; Owner: bahadirgolcuk
--

ALTER TABLE ONLY public.labels
    ADD CONSTRAINT labels_pk PRIMARY KEY (label_id);


--
-- TOC entry 3543 (class 2606 OID 16463)
-- Name: detections detections_images_fk; Type: FK CONSTRAINT; Schema: public; Owner: bahadirgolcuk
--

ALTER TABLE ONLY public.detections
    ADD CONSTRAINT detections_images_fk FOREIGN KEY (image_id) REFERENCES public.images(image_id);


--
-- TOC entry 3544 (class 2606 OID 16468)
-- Name: detections detections_labels_fk; Type: FK CONSTRAINT; Schema: public; Owner: bahadirgolcuk
--

ALTER TABLE ONLY public.detections
    ADD CONSTRAINT detections_labels_fk FOREIGN KEY (label_id) REFERENCES public.labels(label_id);


--
-- TOC entry 3540 (class 2606 OID 16415)
-- Name: devices devices_device_types_fk; Type: FK CONSTRAINT; Schema: public; Owner: bahadirgolcuk
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_device_types_fk FOREIGN KEY (device_type_id) REFERENCES public.device_types(device_type_id);


--
-- TOC entry 3541 (class 2606 OID 16420)
-- Name: devices devices_factories_fk; Type: FK CONSTRAINT; Schema: public; Owner: bahadirgolcuk
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_factories_fk FOREIGN KEY (factory_id) REFERENCES public.factories(factory_id);


--
-- TOC entry 3539 (class 2606 OID 16398)
-- Name: factories factories_companies_fk; Type: FK CONSTRAINT; Schema: public; Owner: bahadirgolcuk
--

ALTER TABLE ONLY public.factories
    ADD CONSTRAINT factories_companies_fk FOREIGN KEY (company_id) REFERENCES public.companies(company_id);


--
-- TOC entry 3542 (class 2606 OID 16432)
-- Name: images images_devices_fk; Type: FK CONSTRAINT; Schema: public; Owner: bahadirgolcuk
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_devices_fk FOREIGN KEY (device_id) REFERENCES public.devices(device_id);


-- Completed on 2024-09-29 20:22:27 +03

--
-- PostgreSQL database dump complete
--

-- Completed on 2024-09-29 20:22:27 +03

--
-- PostgreSQL database cluster dump complete
--

