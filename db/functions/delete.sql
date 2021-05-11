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