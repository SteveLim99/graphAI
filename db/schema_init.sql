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
-- Name: getall(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.getall() RETURNS TABLE(id integer, name character varying, gtype character varying, context text, arr text, ent text, nx text, probs numeric[])
    LANGUAGE plpgsql
    AS $$
	begin 
		return query 
			select files.id, files.name, g.gtype, g.context, im.arr, im.ent, im.nx, p.probs from files
			left join(
				select prediction.id, gt.gtype, gt.context from prediction
				left join(
					select graph_types.gid, graph_types.gtype, graph_types.context from graph_types
				) as gt
				on prediction.gid = gt.gid
			) as g
			on files.id = g.id 
			left join(
				select images.id, images.arr, images.ent, images.nx from images 
			) as im 
			on files.id = im.id
			left join(
				select pb.id, array_agg(pb.prob) as probs
				from (
					select probability.id, probability.prob from probability 
					order by gid
				) as pb 
				group by(pb.id)
			) as p
			on files.id = p.id
			group by files.id, g.gtype, g.context, im.arr, im.ent, im.nx, p.probs;
end;$$;


ALTER FUNCTION public.getall() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: downloads; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.downloads (
    id integer NOT NULL,
    arr_file bytea,
    ent_file bytea,
    nx_file bytea
);


ALTER TABLE public.downloads OWNER TO postgres;

--
-- Name: files; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.files (
    id integer NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE public.files OWNER TO postgres;

--
-- Name: files_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.files ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.files_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: graph_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.graph_types (
    gid integer NOT NULL,
    gtype character varying(20) NOT NULL,
    context text NOT NULL
);


ALTER TABLE public.graph_types OWNER TO postgres;

--
-- Name: graph_types_gid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.graph_types ALTER COLUMN gid ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.graph_types_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.images (
    id integer NOT NULL,
    arr text,
    ent text,
    nx text
);


ALTER TABLE public.images OWNER TO postgres;

--
-- Name: prediction; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prediction (
    id integer NOT NULL,
    gid integer NOT NULL
);


ALTER TABLE public.prediction OWNER TO postgres;

--
-- Name: probability; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.probability (
    idx integer NOT NULL,
    id integer NOT NULL,
    gid integer NOT NULL,
    prob numeric
);


ALTER TABLE public.probability OWNER TO postgres;

--
-- Name: probability_idx_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.probability ALTER COLUMN idx ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.probability_idx_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: downloads downloads_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.downloads
    ADD CONSTRAINT downloads_pkey PRIMARY KEY (id);


--
-- Name: files files_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_pkey PRIMARY KEY (id);


--
-- Name: graph_types graph_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.graph_types
    ADD CONSTRAINT graph_types_pkey PRIMARY KEY (gid);


--
-- Name: images images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (id);


--
-- Name: prediction prediction_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction
    ADD CONSTRAINT prediction_pkey PRIMARY KEY (id);


--
-- Name: probability probability_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.probability
    ADD CONSTRAINT probability_pkey PRIMARY KEY (idx);


--
-- Name: downloads downloads_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.downloads
    ADD CONSTRAINT downloads_id_fkey FOREIGN KEY (id) REFERENCES public.files(id);


--
-- Name: images images_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_id_fkey FOREIGN KEY (id) REFERENCES public.files(id);


--
-- Name: prediction prediction_gid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction
    ADD CONSTRAINT prediction_gid_fkey FOREIGN KEY (gid) REFERENCES public.graph_types(gid);


--
-- Name: prediction prediction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction
    ADD CONSTRAINT prediction_id_fkey FOREIGN KEY (id) REFERENCES public.files(id);


--
-- Name: probability probability_gid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.probability
    ADD CONSTRAINT probability_gid_fkey FOREIGN KEY (gid) REFERENCES public.graph_types(gid);


--
-- Name: probability probability_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.probability
    ADD CONSTRAINT probability_id_fkey FOREIGN KEY (id) REFERENCES public.files(id);


--
-- PostgreSQL database dump complete
--

