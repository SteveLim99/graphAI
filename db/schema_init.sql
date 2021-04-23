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
-- Name: delete_prediction(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.delete_prediction(input_id integer DEFAULT NULL::integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
	begin
		DELETE FROM downloads where downloads.id = input_id;
		DELETE FROM images where images.id = input_id;
		DELETE FROM prediction where prediction.id = input_id;
		DELETE FROM probability where probability.id = input_id;
		DELETE FROM files WHERE files.ID  = input_id;
end;$$;


ALTER FUNCTION public.delete_prediction(input_id integer) OWNER TO postgres;

--
-- Name: getall(integer, text, date, date, integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.getall(result_offset integer DEFAULT 0, keyword text DEFAULT NULL::text, start_year date DEFAULT NULL::date, end_year date DEFAULT NULL::date, graph_type integer DEFAULT NULL::integer, input_uid integer DEFAULT NULL::integer) RETURNS TABLE(id integer, name character varying, input_date timestamp without time zone, gtype character varying, context text, arr text, ent text, nx text, probs numeric[])
    LANGUAGE plpgsql
    AS $$
	begin 
		return query 
			select files.id, files.name, files.input_date, g.gtype, g.context, im.arr, im.ent, im.nx, p.probs from files
			left join(
				select prediction.id, gt.gid, gt.gtype, gt.context from prediction
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
			where 
			(keyword ISNULL OR files.name ilike concat(keyword,'%'))
			and 
			(start_year ISNULL or files.input_date::date >= start_year)
			and
			(end_year ISNULL or files.input_date::date <= end_year)
			and
			(graph_type ISNULL or g.gid = graph_type)
			and
			(files.uid = input_uid)
			group by files.id, g.gtype, g.context, im.arr, im.ent, im.nx, p.probs;
end;$$;


ALTER FUNCTION public.getall(result_offset integer, keyword text, start_year date, end_year date, graph_type integer, input_uid integer) OWNER TO postgres;

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
-- Name: expired_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expired_tokens (
    tid integer NOT NULL,
    uid integer NOT NULL,
    token text NOT NULL,
    expiry_date timestamp without time zone NOT NULL
);


ALTER TABLE public.expired_tokens OWNER TO postgres;

--
-- Name: expired_tokens_tid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.expired_tokens ALTER COLUMN tid ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.expired_tokens_tid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: files; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.files (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    input_date timestamp without time zone,
    uid integer NOT NULL
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
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    uid integer NOT NULL,
    uname character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    pw text NOT NULL,
    register_date timestamp without time zone NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_uid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.users ALTER COLUMN uid ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.users_uid_seq
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
-- Name: expired_tokens expired_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expired_tokens
    ADD CONSTRAINT expired_tokens_pkey PRIMARY KEY (tid);


--
-- Name: expired_tokens expired_tokens_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expired_tokens
    ADD CONSTRAINT expired_tokens_token_key UNIQUE (token);


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
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (uid);


--
-- Name: downloads downloads_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.downloads
    ADD CONSTRAINT downloads_id_fkey FOREIGN KEY (id) REFERENCES public.files(id);


--
-- Name: expired_tokens expired_tokens_uid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expired_tokens
    ADD CONSTRAINT expired_tokens_uid_fkey FOREIGN KEY (uid) REFERENCES public.users(uid);


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
-- Name: files uid; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT uid FOREIGN KEY (uid) REFERENCES public.users(uid);


--
-- PostgreSQL database dump complete
--

