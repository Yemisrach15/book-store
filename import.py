# import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os
import csv

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine)) 

file = open('books.csv', 'r')
books = csv.reader(file)
next(books)
i = 0
limit=100
for isbn, title,author, year in books:
    db.execute("insert into books (isbn, title, author, year) values (:isbn, :title, :author, :year);",{'isbn':isbn, 'title':title, 'author':author, 'year':year})
    print(i+1,title,"uploading...")
    i+=1
    if i==limit:
        db.commit()
        print("\nuploaded",limit,"books\n")
        limit += 100
                     
db.commit()
file.close()
print("Uploading Finished.Total uploaded",i)

# try:
#     connection = psycopg2.connect(host="ec2-107-22-245-82.compute-1.amazonaws.com", database="d2dcrcfq11qljh", user="xjnywjccjpeakj",password="247510e9deb24b34c236a022343ada3f8eb5bad0994d3974bb89f60c89c36d1e")

#     f = open(r'books.csv', 'r')

#     if connection is not None:
#         print("Connection established to Heroku postgresql.")
#     if f is not None:
#         print("CSV file opened in read mode.")

#     cur = connection.cursor()
#     cur.copy_from(f, table="books", columns=('isbn', 'title', 'author', 'year'), sep=',')

# except (Exception, psycopg2.DatabaseError) as error:
#     print(error)

# finally:
#     if connection is not None:
#         connection.close()
#         print("Connection closed to Heroku postgresql.")
#     if f is not None:
#         f.close()
#         print("CSV file closed in read mode.")
