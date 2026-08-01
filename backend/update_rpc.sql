create or replace function hybrid_search_documents(
  query_text text,
  query_embedding vector(384),
  match_count int,
  full_text_weight float default 1,
  semantic_weight float default 1,
  rrf_k int default 50
) returns setof documents
language plpgsql
as $function
declare
  fts_query tsquery;
begin
  -- Convert natural language to tsquery using plainto_tsquery (which strips punctuation safely),
  -- then convert it to text, replace the AND operators (&) with OR operators (|), and cast back to tsquery.
  fts_query := replace(plainto_tsquery('english', query_text)::text, '&', '|')::tsquery;
  
  return query
  with fts_search as (
    select id, rank() over (order by ts_rank(fts, fts_query) desc) as rank_ix
    from documents
    where fts @@ fts_query
    limit 100
  ),
  semantic_search as (
    select id, rank() over (order by embedding <=> query_embedding) as rank_ix
    from documents
    limit 100
  )
  select documents.*
  from documents
  join (
    select
      coalesce(semantic_search.id, fts_search.id) as id,
      coalesce(1.0 / (semantic_weight + semantic_search.rank_ix), 0.0) +
      coalesce(1.0 / (full_text_weight + fts_search.rank_ix), 0.0) as score
    from semantic_search
    full outer join fts_search on semantic_search.id = fts_search.id
    order by score desc
    limit match_count
  ) as rrf on documents.id = rrf.id
  order by rrf.score desc;
end;
$function;
