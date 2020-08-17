FROM postgres:12.4

# init scripts before postgres starts
COPY init/1-create_tables.sql /docker-entrypoint-initdb.d/
COPY init/2-populate_data.sql /docker-entrypoint-initdb.d/
COPY init/3-create_views.sql /docker-entrypoint-initdb.d/