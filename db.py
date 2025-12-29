# create a database using sqlite3
# import sqlite3
# conn = sqlite3.connect('dbname.db')
# cursor = conn.cursor()
# write the query to create a table
# conn.commit()
# conn.close()

import sqlite3

conn = sqlite3.connect('blog.db')

cursor = conn.cursor()
#Create users table

cursor.execute(''' CREATE TABLE IF NOT EXISTS blogs(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    title TEXT,
    image TEXT,
    description TEXT)''')

# cursor.execute(''' INSERT INTO blogs (title, image, description) 
#                VALUES (?, ?, ?)''', 
#                ('Demo', 'image.jpg', 'This is my blog'))

cursor.execute('''CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                username TEXT,
                email TEXT,
                password BLOB) ''')

cursor.execute('''CREATE TABLE IF NOT EXISTS comments(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                blog_id INTEGER,
                comment TEXT,
                user_id INTEGER) ''')

# cursor.execute("ALTER TABLE blogs ADD COLUMN author TEXT;")
# cursor.execute("ALTER TABLE blogs ADD COLUMN date_published TEXT;")
cursor.execute('''alter table blogs add column user_id integer''')

conn.commit()
conn.close()  


