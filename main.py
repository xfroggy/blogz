from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:MyNewPass@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(600))
    completed = db.Column(db.Boolean)

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.completed = False

@app.route('/')
def index():
    return redirect('/blog')

@app.route('/newpost')
def first_newpost():
    return render_template('newpost.html', title="Add a Blog")       

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-body']
        new_blog = Blog(blog_title, blog_body)
        db.session.add(new_blog)
        db.session.commit()
    return redirect('/blog')    
    
@app.route('/blog', methods=['POST', 'GET'])
def blog_index():
    blogs = Blog.query.filter_by(completed=False).all()
    completed_blogs = Blog.query.filter_by(completed=True).all()
    return render_template('blog.html',title="Build a Blog", 
        blogs=blogs, completed_blogss=completed_blogs)


@app.route('/delete-blog', methods=['POST'])
def delete_blog():

    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    blog.completed = True
    db.session.add(blog)
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run()