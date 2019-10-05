from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:MyNewPass@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'z337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(600))
    completed = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.completed = False
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogz = db.relationship('Blog', backref = 'owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    print(session)
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')



@app.route('/signup')
def initial_signup():
    return render_template('signup.html', title="Initial Signup")

@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    username = request.form['username']
    password = request.form['password']
    verify = request.form['verify']

    verify_error = ""
    validator1 = False
    validator2 = False 

    username_error = isValid(username, "Username")
    if username_error == "":
        username_error = spaceCheck(username, "Username")
    
    password_error = isValid(password, "Password")
    if password_error == "":
        password_error = spaceCheck(password, "Password")

    if (not verify) or (verify.strip() == ""):
            verify_error = "Passwords don't match"    

    if  verify != password:
        verify_error = "Passwords don't match"            

    if username_error == "" and password_error == "" and verify_error == "":
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('signup.html', username_error = "User already exists, please go to login page")

        new_user = User(username, password)

        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return redirect('/newpost')
  

    return render_template("signup.html", 
        username_error=username_error, password_error=password_error, 
        verify_error=verify_error, 
        username=username, title="User Sign Up")

def isValid(item, name):
    if (not item) or (item.strip() == "") or (len(item) < 3) or (len(item) > 19) :
        return "Not a valid "+name
    else:
        return ""  

def spaceCheck(item, name):
    for i in item:
        if i == " ":
            return "Not a valid "+ name
    return ""      

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        elif user and user.password != password:
            flash('Username password incorrect', 'error')
            return redirect('/login')
        else:
            flash('Username does not exist', 'error')    
            # TODO - explain why login failed
            #flash('User password incorrect, or user does not exist', 'error')
        


    return render_template('login.html')    

@app.route('/newpost')
def first_newpost():
    return render_template('newpost.html', title="Add a Blog")       

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    
    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-body']
        if blog_title == "" or blog_body == "":   
            if blog_title == "":
                flash('Please fill in the title', 'title_error')  
            if blog_body == "":
                flash('Please fill in the body', 'body_error') 
            return redirect('/newpost')   
        else:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            blog_detail = False
            title = ""
           
            return render_template('blog.html',title=title, blog_detail=blog_detail, blog_post =  Blog.query.filter_by(id=new_blog.id).all())   





@app.route('/blog')
def blog_index():
    #blogs = Blog.query.filter_by(completed=False).all()
    username = request.args.get('username')
    blogs = Blog.query.order_by(desc(Blog.id)).all()
    completed_blogs = Blog.query.filter_by(completed=True).all() 
    id = request.args.get("id")

    blog_post = Blog.query.filter_by(id=id)
    if id == None:
        blog_detail = True
        title="Build a Blog" 
    else:
        blog_detail = False    
        title=""
    return render_template('blog.html',title=title, blog_detail=blog_detail, blogs=blogs, completed_blogs=completed_blogs, blog_post=blog_post, username=username)   


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/', methods=['GET'])
def index():
    all_users = User.query.all()
    return render_template('index.html', all_users = all_users)

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