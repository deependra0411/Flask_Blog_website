from flask import Flask, render_template, request, redirect, url_for,session,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import math
import os
from werkzeug.utils import secure_filename
import json


with open ('config.json','rt') as f:     # reading json file. 
    para=json.load(f)["parameter"]

app=Flask(__name__)  # Object instatntiation

app.secret_key='super-secret-key'  # Secret key for session.

app.config['SQLALCHEMY_DATABASE_URI'] = para['local_uri']    # Connecting to database.

app.config['upload_folder'] = para['upload_location']    # config upload folder.

db = SQLAlchemy(app)   # db as an instance of object sqlAlchemy database object.

class POSTS(db.Model):
    sno = db.Column(db.Integer,primary_key=True,unique=True)
    title = db.Column(db.String(200))
    tagline = db.Column(db.String(100))
    slug = db.Column(db.String(25))
    content = db.Column(db.Text)
    img_file = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.now())

class CONTACT(db.Model):
    sno = db.Column(db.Integer,primary_key=True,unique=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(200))
    message = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.now())
  

@app.route('/',methods=['GET','POST'])      # Decorator for Home Page
def home():
    posts=POSTS.query.filter_by().all()
    last =math.ceil(len(posts)/para['no_of_post'])
    page=request.args.get('page')
    if(not str(page).isnumeric()):
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

@app.route('/uploader',methods=['GET','POST'])                          # Uploader 
def uploader():
    if 'user' in session and session['user'] == para['user']:
        f = request.files['file1']
        if f:
            try:
                f.save(os.path.join(app.config['upload_folder'], secure_filename(f.filename)))
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
    if ('user' in session and session['user']==para['user'] ):
        posts=POSTS.query.filter_by().all()
        return render_template('dashboard.html',para=para,posts=posts)
    else:
        return redirect(url_for('login'))
    
@app.route('/logout')                  # Logout page
def logout():
    session.pop('user')
    flash('Logout successful!', 'success')
    return redirect(url_for('dashboard'))
    
@app.route('/login' ,methods=['GET','POST'])                                       # Login page
def login():
    if ('user' in session and session['user']==para['user'] ):
        return redirect(url_for('dashboard'))

    if request.method=="POST":
        email_address = request.form.get("email_id")
        password = request.form.get("email_pass")
        if email_address == para['user'] and password == para['pass']:
            session['user'] = email_address
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Invalid credentials.', 'danger')
            return redirect(url_for('login'))
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
    if ('user' in session and session['user']==para['user'] ):
        post=POSTS.query.filter_by(slug=post_slug).first()
        db.session.delete(post)
        db.session.commit()
        flash('Deleted successfully','success')
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/edit/<string:post_slug>',methods=['POST','GET'])     # Editing Post
def edit(post_slug):
    if ('user' in session and session['user']==para['user'] ):
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
    if ('user' in session and session['user']==para['user'] ):
        if request.method=="POST":
            try:
                title=request.form.get('title')
                tagline=request.form.get('tagline')
                slug=request.form.get('slug')
                content=request.form.get('content')
                img_file=request.form.get('image')
                entry=POSTS(
                    title=title,
                    tagline=tagline,
                    slug=slug,
                    content=content,
                    img_file=img_file,
                    date=datetime.now()
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