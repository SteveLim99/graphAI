CREATE or replace FUNCTION public.getall(
	result_offset integer default 0,
	keyword text default null,
	start_year date default null,
	end_year date default null,
	graph_type integer default null
) RETURNS TABLE(id integer, name character varying, input_date timestamp without time zone, gtype character varying, context text, arr text, ent text, nx text, probs numeric[])
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
			group by files.id, g.gtype, g.context, im.arr, im.ent, im.nx, p.probs;
end;$$;