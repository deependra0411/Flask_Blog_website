from flask import Flask, render_template, request, redirect, url_for,session,flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from datetime import datetime
import math
from flask_bcrypt import Bcrypt 
import os
from werkzeug.utils import secure_filename
import json


with open ('config.json','rt') as f:     # reading json file. 
    para=json.load(f)["parameter"]

app=Flask(__name__)  # Object instatntiation

app.secret_key=para['secret_key']  # Secret key for sessions.

app.WTF_CSRF_SECRET_KEY=para['csrf_secret_key']   # Form protection

app.config['SQLALCHEMY_DATABASE_URI'] = para['local_uri']    

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024      # Max content size of upload

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}  # Allowed extension for file uploading

app.config['UPLOAD_FOLDER'] = para['upload_location']    # config upload folder.

csrf = CSRFProtect(app)     

bcrypt = Bcrypt(app)  

db = SQLAlchemy(app)   

class POSTS(db.Model):
    sno = db.Column(db.Integer,primary_key=True,unique=True)
    title = db.Column(db.String(200))
    tagline = db.Column(db.String(100))
    slug = db.Column(db.String(25))
    content = db.Column(db.Text)
    img_file = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.now())
    UserID=db.Column(db.String(255),unique=True,nullable=False)
    author=db.Column(db.String(255),nullable=False)

class CONTACT(db.Model):
    sno = db.Column(db.Integer,primary_key=True,unique=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(200))
    message = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.now())

class Users(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(200),nullable=False)
    userid=db.Column(db.String(200),unique=True,nullable=False)
    password=db.Column(db.String(200),nullable=False)

def allowed_file(filename):                                # function to define aloowed extensions
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

   
@app.route('/singup',methods=['GET','POST'])        #Singup Route
def singup():
    if request.method=="POST":
        try:
            name=request.form.get('Name')
            email=request.form.get('email_id')
            password=request.form.get('email_pass') 

            entry=Users(
                name=name,
                userid = email,
                password = bcrypt.generate_password_hash (password).decode('utf-8') 
                )
            db.session.add(entry)
            db.session.commit()
            flash('User registered successfully','success')
            return redirect(url_for('login'))
        except Exception:
            flash('All fileds are mandatory', 'error')
            db.session.rollback()
            return redirect(url_for('singup'))
        finally:
            db.session.close()

    return render_template('singup.html',para=para)

@app.route('/',methods=['GET','POST'])      # Home Page with paginiation
def home():
    posts=POSTS.query.filter_by().all()
    last =math.ceil(len(posts)/para['no_of_post'])
    page=request.args.get('page')  # Getting page from URL
    if(not str(page).isnumeric()): # if nothing in the URL then setting the page to 1
        page=1
    page=int(page)
    posts=posts[(page-1)*int(para['no_of_post']) : (page-1)*int(para['no_of_post'])+int(para['no_of_post'])]
    if(page==1):
        prev = '#'
        next = '/?page='+ str(page+1)
    elif(page==last):
        prev = '/?page='+ str(page-1)
        next = '#'
    else:
        prev = '/?page='+ str(page-1)
        next = '/?page='+ str(page+1)
    
    return render_template('index.html',para=para,posts=posts,prev=prev,next=next)

@app.route('/uploader', methods=['GET', 'POST'])         # uploader
def uploader():
    if 'user' in session:
        f = request.files.getlist('file1')
        if f:
            try:
                for g in f:
                    if allowed_file(g.filename):
                        g.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(g.filename)))
                    else:
                        flash('Invalid file type', 'error')
                        return redirect(request.url)
                flash('File uploaded successfully', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f'Error uploading file: {str(e)}', 'error')
        else:
            flash('No file selected', 'error')
    else:
        flash('Unauthorized access', 'error')

    return redirect(url_for('dashboard'))


@app.route('/contact',methods=['POST','GET'])                       # Contact
def contact():
    if request.method=="POST":
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone') 
        message=request.form.get('message')

        entry=CONTACT(
            name=name,
            email = email,
            phone = phone,
            message = message,
            date = datetime.now()
                )
        db.session.add(entry)
        db.session.commit()
        flash('Message send successfully','success')
        return redirect(url_for('contact'))
    return render_template('contact.html',para=para)

@app.route('/dashboard')
def dashboard():
    if ('user' in session  ):
        if session['user']==para['user']:
            posts=POSTS.query.filter_by().all()
            return render_template('dashboard.html',para=para,posts=posts)

        posts=POSTS.query.filter_by(UserID=session['user']).all()
        return render_template('dashboard.html',para=para,posts=posts)
    else:
        return redirect(url_for('login'))
    
@app.route('/logout')                  # Logout page
def logout():
    session.pop('user')
    flash('Logout successful!', 'success')
    return redirect(url_for('dashboard'))
    
@app.route('/login' ,methods=['GET','POST'])          # Login page
def login():
    if ('user' in session ):
        return redirect(url_for('dashboard'))

    if request.method=="POST":
        try:
            email_address = request.form.get("email_id")
            password = request.form.get("email_pass")
            user=Users.query.filter_by(userid=email_address).first()    

            is_valid = bcrypt.check_password_hash(user.password, password) 

            if email_address == user.userid and is_valid:
                session['user'] = user.userid
                # return f"Password: {password}<br>Hashed Password:{user.password}<br>Is Valid: {is_valid}<br>userid:{email_address}<br>session_user:{[session['user']]}"
                return redirect(url_for('dashboard'))
            else:
                flash('Login failed. Invalid credentials.', 'danger')
                return redirect(url_for('login'))
        except Exception:
            flash('No user exists','danger')
            return redirect(url_for('singup'))
            

    return render_template('login.html',para=para)

@app.route('/about')                                             # About page
def about():
    return render_template('about.html',para=para)

@app.route('/post/<string:post_slug>',methods=['POST','GET'])        # For showing content of selected post.
def post(post_slug):
    post=POSTS.query.filter_by(slug=post_slug).first()
    return render_template('post.html',para=para,post=post)

@app.route('/delete/<string:post_slug>',methods=['POST','GET'])        # For Deleting selected post.
def delete(post_slug):
    if ('user' in session  ):
        post=POSTS.query.filter_by(slug=post_slug).first()
        db.session.delete(post)
        db.session.commit()
        flash('Deleted successfully','success')
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/edit/<string:post_slug>',methods=['POST','GET'])     # Editing selected Post
def edit(post_slug):
    if ('user' in session  ):
        post=POSTS.query.filter_by(slug=post_slug).first()
        if request.method=='POST':
            
            title=request.form.get('title')
            tagline=request.form.get('tagline')
            slug=request.form.get('slug')
            content=request.form.get('content')
            img_file=request.form.get('image')

            post.title=title
            post.tagline=tagline
            post.slug=slug
            post.content=content
            post.img_file=img_file

            db.session.commit()
            flash('Edited successfully','success')
            return redirect(url_for('dashboard'))
    
        return render_template('edit.html',para=para,post=post)
    else:
        return redirect(url_for('login'))


@app.route('/add',methods=['POST','GET'])     # Adding New Post
def add():
    if ('user' in session  ):
        user=Users.query.filter_by(userid=session['user']).first() 
        if request.method=="POST":
            try:
                title=request.form.get('title')
                tagline=request.form.get('tagline')
                slug=request.form.get('slug')
                content=request.form.get('content')
                img_file=request.form.get('image')
                UID=session['user']
                Author=user.name
                entry=POSTS(
                    title=title,
                    tagline=tagline,
                    slug=slug,
                    content=content,
                    img_file=img_file,
                    date=datetime.now(),
                    UserID=UID,
                    author=Author
                )
                db.session.add(entry)
                db.session.commit()
                flash('Added successfully','success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash('Failed','danger')
                return f"An error occurred: {str(e)}"
            finally:
                db.session.close()

        return render_template('add.html',para=para)
    else:
        return redirect(url_for('login'))
    


if __name__=='__main__':
    app.run(debug=True)
