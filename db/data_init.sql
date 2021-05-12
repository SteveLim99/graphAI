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
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (uid, uname, email, pw, register_date) FROM stdin;
5	test1	a1@gmail.com	$2b$12$aiITqcFXEi0xUVy2ROCHyurnXU4on7Hp0gmqIuYe7lD6rztolfT7S	2021-04-22 16:02:36
7	nekonays	nekonays99@gmail.com	$2b$12$LOHTseUER3GalyAVCrVGcu7RcTfljN311vhk5ryjEXOCLhvD6GQ4u	2021-04-23 09:12:42
8	steve	test@gmail.com	$2b$12$vS0e18WGIehEXpkTApPSB.62mqn.dp6qyC/OR4MzbVEGoy69d.F9O	2021-04-23 15:31:04
9	zzzz	limzisheng03@gmail.com	$2b$12$nMpJUjfVOVr0GBzT1tWrE.ePMQcTrgh/ig/8P1na6YpLkavWOro8W	2021-04-24 10:37:37
10	demo	demo@gmail.com	$2b$12$kmsbg04k5GLCyRQF4wO36u/RTikz5ioMrpqwaqalEseOiPtvn/ZA6	2021-04-26 12:29:31
11	demo1	demo1@gmail.com	$2b$12$YSJXSTT4VY0Gi97GX4z9qecYb9vmHOv6fqytTEzfT2wGuLlzyhP4O	2021-04-26 12:41:21
12	demo2	demo2@gmail.com	$2b$12$k7gOkpI7Q2vuC/OiahxAH.7PiyQG7Z9tPyF6.BM3/cg7UNnd.HyFO	2021-04-26 13:08:23
13	demotest	demotest@gmail.com	$2b$12$m7T41/Qq6r2HbvwTl0y3wuaIwRqzahjK0KBQ/OraZrRjQ8S0ZYmdu	2021-04-26 13:16:16
\.


--
-- Data for Name: expired_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expired_tokens (tid, uid, token, expiry_date) FROM stdin;
\.


--
-- Data for Name: graph_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.graph_types (gid, gtype, context) FROM stdin;
1	BPMN	Business Process Model and Notation is a graphical representation for specifying business processes in a business process model. Originally developed by the Business Process Management Initiative, BPMN has been maintained by the Object Management Group since the two organizations merged in 2005.
2	Swimlane	A swimlane diagram is a type of flowchart that delineates who does what in a process. Using the metaphor of lanes in a pool, a swimlane diagram provides clarity and accountability by placing process steps within the horizontal or vertical “swimlanes” of a particular employee, work group or department.
\.


--
-- Data for Name: prediction; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.prediction (id, name, input_date, uid, gid) FROM stdin;
\.


--
-- Data for Name: files; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.files (id, arr_file, ent_file, nx_file, nx_png_file) FROM stdin;
\.


--
-- Data for Name: probability; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.probability (pid, id, gid, prob) FROM stdin;
\.


--
-- Name: expired_tokens_tid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.expired_tokens_tid_seq', 48, true);


--
-- Name: graph_types_gid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.graph_types_gid_seq', 2, true);


--
-- Name: prediction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.prediction_id_seq', 1, false);


--
-- Name: probability_pid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.probability_pid_seq', 1, false);


--
-- Name: users_uid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_uid_seq', 13, true);


--
-- PostgreSQL database dump complete
--

