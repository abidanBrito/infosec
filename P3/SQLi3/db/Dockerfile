# A MySQL container.
FROM mysql:5.7

ADD db.sql /docker-entrypoint-initdb.d

EXPOSE 3306
CMD ["mysqld", "--early-plugin-load=keyring_file=keyring_file.so"]
