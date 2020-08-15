CREATE TABLE books
(
    uid bigserial,
    title text NOT NULL,
    publisher text NOT NULL,
    publish_year smallint NOT NULL,
    author text NOT NULL,
    acquire_date date NOT NULL,
    issue_count integer NOT NULL,
    PRIMARY KEY (uid)
);

ALTER TABLE books OWNER to postgres;