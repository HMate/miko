CREATE MATERIALIZED VIEW author_book_count AS
SELECT author, SUM(issue_count) as book_count
FROM books
GROUP BY author;

CREATE MATERIALIZED VIEW publisher_book_count AS
SELECT publisher, SUM(issue_count) as book_count FROM books
GROUP by publisher;

CREATE MATERIALIZED VIEW average_acquire_date AS
SELECT to_timestamp(SUM(extract(epoch from acquire_date)*issue_count) / SUM(issue_count))::date as avg_acquire
FROM books;

/* Query presumes that acquire_date was given in the same timezone as the current_date function */
CREATE VIEW average_books_age AS
SELECT justify_interval((current_date - avg_acquire) * interval '1 days') as age
FROM average_acquire_date;

CREATE MATERIALIZED VIEW oldest_youngest_books AS
(SELECT 'oldest' as tag, title, acquire_date FROM books order by acquire_date asc limit 1)
UNION
(SELECT 'youngest' as tag, title, acquire_date FROM books order by acquire_date desc limit 1);

CREATE MATERIALIZED VIEW author_books_until_year AS
SELECT year, author, MAX(book_count) as books FROM (
	SELECT extract(year from acquire_date)::smallint AS year, author,
	SUM(issue_count) OVER (PARTITION BY author order by acquire_date) AS book_count
	FROM books) as books_per_year
GROUP BY year, author;

CREATE MATERIALIZED VIEW author_average_acquire AS
SELECT author, justify_interval(AVG(acquire_date - publish_year) * interval '1 day') as avg_acquire FROM (
	SELECT title, author, min(acquire_date) as acquire_date, to_date(publish_year::text, 'YYYY') as publish_year
	FROM books
	GROUP BY title, author, publish_year) as FirstAcquire
GROUP BY author;

CREATE MATERIALIZED VIEW author_third_book_issues AS
SELECT author, title, issue_count from books
INNER JOIN (
	SELECT NTH_VALUE(uid, 3) OVER (PARTITION BY author order by publish_year) AS third_book_uid
	from books
) as B2 ON (B2.third_book_uid = uid)
where B2.third_book_uid IS NOT NULL
	GROUP BY author, title, issue_count;

CREATE OR REPLACE FUNCTION refresh_book_views()
  RETURNS TRIGGER LANGUAGE plpgsql
  AS $$
  BEGIN
  REFRESH MATERIALIZED VIEW author_book_count;
  REFRESH MATERIALIZED VIEW publisher_book_count;
  REFRESH MATERIALIZED VIEW average_acquire_date;
  REFRESH MATERIALIZED VIEW oldest_youngest_books;
  REFRESH MATERIALIZED VIEW author_books_until_year;
  REFRESH MATERIALIZED VIEW author_average_acquire;
  REFRESH MATERIALIZED VIEW author_third_book_issues;
  RETURN NULL;
  END $$;

CREATE TRIGGER refresh_stats
  AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE
  ON books
  FOR EACH STATEMENT
  EXECUTE PROCEDURE refresh_book_views();