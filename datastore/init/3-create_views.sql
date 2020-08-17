CREATE MATERIALIZED VIEW author_book_count AS
SELECT author, SUM(issue_count) as book_count
FROM books
GROUP BY author;

CREATE MATERIALIZED VIEW publisher_book_count AS
SELECT publisher, SUM(issue_count) as book_count FROM books
GROUP by publisher;

CREATE MATERIALIZED VIEW average_acquire_date AS
SELECT to_timestamp(SUM(extract(epoch from acquire_date)*issue_count) / SUM(issue_count))::date as avg_acquire FROM books;

CREATE MATERIALIZED VIEW oldest_youngest_books AS
(select 'oldest', title, acquire_date FROM books order by acquire_date asc limit 1)
UNION
(select 'youngest', title, acquire_date FROM books order by acquire_date desc limit 1);

CREATE MATERIALIZED VIEW author_books_until_year AS
SELECT year, author, MAX(book_count) FROM (
	SELECT extract(year from acquire_date)::smallint AS year, author,
	SUM(issue_count) OVER (PARTITION BY author order by acquire_date) AS book_count
	FROM books) as books_per_year
GROUP BY year, author;

CREATE OR REPLACE FUNCTION refresh_book_views()
  RETURNS TRIGGER LANGUAGE plpgsql
  AS $$
  BEGIN
  REFRESH MATERIALIZED VIEW author_book_count;
  REFRESH MATERIALIZED VIEW publisher_book_count;
  REFRESH MATERIALIZED VIEW average_acquire_date;
  REFRESH MATERIALIZED VIEW oldest_youngest_books;
  REFRESH MATERIALIZED VIEW author_books_until_year;
  RETURN NULL;
  END $$;

CREATE TRIGGER refresh_stats
  AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE
  ON books
  FOR EACH STATEMENT
  EXECUTE PROCEDURE refresh_book_views();