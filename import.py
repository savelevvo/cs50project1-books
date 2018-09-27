import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def _prepare_db():
    author = """CREATE TABLE IF NOT EXISTS author (
        id      serial PRIMARY KEY,
        name    varchar(90) UNIQUE
    );"""

    book = """CREATE TABLE IF NOT EXISTS book (
      isbn    VARCHAR(10) PRIMARY KEY,
      title   VARCHAR(255) NOT NULL,
      author  INTEGER NOT NULL,
      release_year    INTEGER,
      FOREIGN KEY (author) REFERENCES author (id) ON DELETE RESTRICT
    );"""

    db.execute(author)
    db.execute(book)
    db.commit()


def _insert_data(isbn, title, author, release_year):
    db.execute("INSERT INTO author (name) VALUES ('{}') ON CONFLICT DO NOTHING;".format(author))
    db.commit()
    author_id = db.execute("SELECT id FROM author WHERE name = '{}';".format(author)).fetchone()[0]
    db.execute("INSERT INTO book (isbn, title, author, release_year) VALUES (:isbn, :title, :author_id, :release_year)",
               {'isbn': isbn, 'title': title, 'author_id': author_id, 'release_year': release_year})
    db.commit()


def main():
    f = open('books-sample.csv', mode='r')
    reader = csv.reader(f)
    reader.__next__()  # skip header

    _prepare_db()

    for isbn, title, author, year in reader:
        _insert_data(isbn, title, author, year)


if __name__ == "__main__":
    main()
