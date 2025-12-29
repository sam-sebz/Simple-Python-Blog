#first create a virtual environment
# python -m venv your environment name
# source your environment name/Scripts/activate
#install flask
# from flask import Flask, render_template
# app = Flask(__name__)
# @app.route('/')
# def index():  
#     return render_template('index.html')
# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask,render_template,request,session,redirect,url_for
import sqlite3
from bcrypt import hashpw,gensalt,checkpw
from datetime import date
import requests


app = Flask(__name__)
app.secret_key = 'your_secret_key'
 
@app.route('/')
def index():
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute(''' SELECT * FROM blogs ''')
    conn.commit()
    blogs = cursor.fetchall()
    conn.close()  
    return render_template('index.html',blogs=blogs) #render the index.html file

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = hashpw(password.encode('utf-8'), gensalt())

        conn = sqlite3.connect('blog.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO USERS (username, email, password) VALUES (?, ?, ?)''',(name,email,hashed_password))
        conn.commit()
        conn.close()
        return render_template('signin.html')
    


        
@app.route('/signin', methods=['GET','POST'])
def signin():  
    if request.method == 'GET':
        if session.get('user_id'):
            return redirect(url_for('index'))
        return render_template('signin.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('blog.db')
        cursor = conn.cursor()
        cursor.execute(''' SELECT * FROM users WHERE email = ? ''', (email,))
        conn.commit()
        user = cursor.fetchone()
        conn.close()

        if user and hashpw(password.encode('utf-8'),user[3]):
            session ['user_id'] = user[0]
            session ['user_name'] = user[1]
            return render_template('index.html')

@app.route('/comment', methods=['POST'])
def comment():
    if not session.get('user_id'):
        return redirect(url_for('signin'))
    blog_id = request.form['blog_id']
    user_id = request.form['user_id']
    comment = request.form['comment']

    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute(''' INSERT INTO comments (blog_id,user_id, comment)
                    VALUES (?,?,?)''',(blog_id,user_id,comment))
    conn.commit()
    conn.close()
    return redirect(url_for('view_blog', blog_id=blog_id))

@app.route('/form - insert', methods=['POST'])
def form_insert():
    action= request.form['action']
    title = request.form['title']
    image = request.form['image']
    description = request.form['description']
    author = session.get('user_name') 
    today = date.today()
    user_id = session.get("user_id")

    if action == 'generate':
        generated_description = generate_blog(title)
        return render_template('new_blog.html',description=generated_description, title=title, image=image)

    
    if action == 'submit':

        conn = sqlite3.connect('blog.db')
        cursor = conn.cursor()


        cursor.execute(''' INSERT INTO blogs (title,image, description ,author ,date_published,user_id)
                        VALUES (?,?,?,?,?,?)''',
                        (title, image, description, author, today,user_id))
        conn.commit()
        conn.close()
        return new_blog()
    
def generate_blog(title):
    prompt = f"Write a detailed blog post about {title} in around 200-300 words"
    response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json"
  },
  json={
    "model": "openrouter/auto", # Optional
    "messages": [
      {
        "role": "user",
        "content": "What is the meaning of life?"
      }
      ]
    }
    )
    return response.json()['choices'][0]['message']['content']



@app.route('/update_blog/<int:blog_id>', methods=['POST'])
def update_blog(blog_id):
    title = request.form['title']
    image = request.form['image']
    description = request.form['description']
    author = session.get('user_name')   
    today = date.today()
    user_id = session.get("user_id")
    action= request.form['action']
    

    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    cursor.execute(''' UPDATE blogs SET title = ? , image = ? , description = ? , author = ?, date_published = ? , user_id = ?  WHERE id=? ''',
                        (title, image, description, author, today,blog_id))
    conn.commit()
    conn.close()
    return my_blog()




@app.route('/my_blog')
def my_blog():  
    if not session.get('user_id'):
        return redirect(url_for('signin'))
    user_id=session.get('user_id')
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute(''' SELECT * FROM blogs where user_id = ?''',(user_id,))
    conn.commit()
    blogs = cursor.fetchall()
    conn.close()  
    return render_template('my_blog.html',blogs=blogs)

@app.route('/new_blog')
def new_blog():  
    if not session.get('user_id'):
        return redirect(url_for('signin'))
    user_id=session.get('user_id')
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute(''' SELECT * FROM blogs where user_id = ?''',(user_id,))
    conn.commit()
    blogs = cursor.fetchall()
    conn.close()  
    return render_template('new_blog.html',blogs=blogs)

@app.route('/view_blog/<int:blog_id>')
def view_blog(blog_id):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute(''' SELECT * FROM blogs where id = ?''',(blog_id,))
    blogs = cursor.fetchone()
    cursor.execute(''' SELECT * FROM comments where blog_id = ?''',(blog_id,))
    comments = cursor.fetchall()
    conn.commit()
    
    conn.close()  
    return render_template('view_blog.html',blogs=blogs,comments=comments)

@app.route('/delete_blog/<int:blog_id>')
def delete_blog(blog_id):
    user_id=session.get('user_id')
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute(''' DELETE FROM blogs where id = ? AND user_id= ?''',(blog_id,user_id,))
    conn.commit()
    conn.close()  
    return render_template('index.html')

@app.route('/Logout')
def logout():
    session.pop('user_id', None)  # Clear session
    return redirect(url_for('signin'))

@app.route('/edit_blog/<int:blog_id>')
def edit_blog(blog_id):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute(''' SELECT * FROM blogs where id = ?''',(blog_id,))
    conn.commit()
    blogs = cursor.fetchone()
    conn.close()  
    return render_template('edit_blog.html',blogs=blogs)

@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('seach_blog')
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute(''' SELECT * FROM blogs WHERE title LIKE ? OR description LIKE ? OR author LIKE ?''',('%'+ search_query +'%','%'+ search_query +'%','%'+ search_query +'%'))
    conn.commit()
    blogs = cursor.fetchall()
    conn.close()  
    return render_template('search.html',blogs=blogs)

if __name__ == '__main__':
    app.run(debug=True)