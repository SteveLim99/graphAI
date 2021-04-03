--
-- PostgreSQL database dump
--

-- Dumped from database version 13.2
-- Dumped by pg_dump version 13.2

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

--
-- Data for Name: files; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.files (id, name) FROM stdin;
\.


--
-- Data for Name: graph_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.graph_types (gid, gtype, context) FROM stdin;
1	BPMN	Business Process Model and Notation is a graphical representation for specifying business processes in a business process model. Originally developed by the Business Process Management Initiative, BPMN has been maintained by the Object Management Group since the two organizations merged in 2005.
2	Swimlane	A swimlane diagram is a type of flowchart that delineates who does what in a process. Using the metaphor of lanes in a pool, a swimlane diagram provides clarity and accountability by placing process steps within the horizontal or vertical “swimlanes” of a particular employee, work group or department.
\.


--
-- Data for Name: images; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.images (id, arr, ent, nx) FROM stdin;
\.


--
-- Data for Name: prediction; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.prediction (id, gid) FROM stdin;
\.


--
-- Data for Name: probability; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.probability (idx, id, gid, prob) FROM stdin;
\.


--
-- Name: files_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.files_id_seq', 57, true);


--
-- Name: graph_types_gid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.graph_types_gid_seq', 2, true);


--
-- Name: probability_idx_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.probability_idx_seq', 6, true);


--
-- PostgreSQL database dump complete
--

