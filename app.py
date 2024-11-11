from sqlalchemy import or_
from flask import Flask, render_template, request, redirect, url_for, flash, session
from Models.model import *
from sqlalchemy.exc import IntegrityError
from datetime import datetime


app=Flask(__name__)
app.config['SECRET_KEY']='East'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///gs_store.sqlite3'
app.config['SQLALCHMEY_TRACK_MODIFICATIONS']=False

db.init_app(app)


#before_first_request:
#db.create_all()

with app.app_context():
    db.create_all()
    

@app.route('/',methods=['GET'])
def home():
    return redirect(url_for('logout'))


@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == "POST":
        username=request.form['username']
        email=request.form['email']
        password=request.form['password']
        admin=False
        
        if request.form.get('admin_key')=="Asharma":
            admin=True
            
        try:
            user=User(username=username,email=email,password=password,admin=admin)#creating a new user
            db.session.add(user)
            db.session.commit()
            flash('Your account created successfully','success')
            return redirect(url_for('login'))
        
        except IntegrityError as e:
            db.session.rollback()
            flash('Username or email already exists!') 
            return redirect (url_for('signup'))
        
    return render_template('signup.html')    #Get req


@app.route('/login',methods=['GET',"POST"])
def login():
    if request.method == "POST":
        username_or_email=request.form['username']
        password=request.form['password']
        
        user=User.query.filter(
            or_(User.username==username_or_email,User.email==username_or_email)).first()
        
        if user and user.password==password:
            session['user_id']=user.id
            return redirect(f'/dashboard/{user.id}')
        
        else:
            error_message="Invalid username or password"
            if not user:
                error_message="No user found with these credentials"
            return render_template('login.html',error_message=error_message)
        
    return render_template('login.html')  



def get_user_admin(curr_login_id):
    if 'user_id' in session and curr_login_id==session['user_id']:
        user=User.query.get(curr_login_id)
        return user.admin
    return False


@app.route('/dashboard/<int:curr_login_id>',methods=['GET'])
def dashboard(curr_login_id):
    if request.method=="GET":
        if 'user_id' in session and session['user_id']==curr_login_id:
            user=User.query.get(curr_login_id)
            if user.admin:
                return redirect(url_for('admin_dashboard',curr_login_id=curr_login_id))
            else:
                return redirect(url_for('customer_dashboard',curr_login_id=curr_login_id))
        
        flash('Please login to access the dashboard')
        return redirect(url_for('logout'))
  
        
@app.route('/admin/<int:curr_login_id>/dashboard',methods=["GET"])
def admin_dashboard(curr_login_id):
    if request.method=="GET":
        if 'user_id' in session and session['user_id']==curr_login_id:
            user=User.query.get(curr_login_id)
            if not user.admin:
                flash('You are not authoriezed to access this dashbaord')
                return redirect(f'/dashboard/{curr_login_id}')
            
            categories=Category.query.all()
            data={'curr_login_id':curr_login_id,
                 'categories':categories} 
           
            return render_template('admin_dashboard.html',data=data,name=User.query.get(curr_login_id).username)
    flash('Please login to access the admin dashboard')
    return redirect(url_for('logout'))
    
    
@app.route('/admin/<int:curr_login_id>/create_category',methods=["GET","POST"])    
def create_category(curr_login_id):
    if not get_user_admin(curr_login_id):
        flash("You are not authorized to access this page")
        return redirect(url_for('logout'))
            
    if request.method=="POST":
        name=request.form['name']  
        
        try:
            category=Category(name=name)
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('admin_dashboard',curr_login_id=curr_login_id))   
        
        except IntegrityError:
            db.session.rollback()
            flash('name is already exists')
            return redirect(url_for('create_category',curr_login_id=curr_login_id))   
            
    return render_template('create_category.html',curr_login_id=curr_login_id)    


@app.route('/admin/<int:curr_login_id>/edit_category/<int:category_id>',methods=["GET","POST"])    
def edit_category(curr_login_id,category_id):
    if not get_user_admin(curr_login_id):
        flash("You are not authorized to access this page")
        return redirect(url_for('logout'))
    
    category=Category.query.get_or_404(category_id)
    
    if request.method=="POST":
        try:
            category.name=request.form['name']
            db.session.commit()
            flash('Category is updated Successfully!')
            return redirect(url_for('admin_dashboard',curr_login_id=curr_login_id,category_id=category.id))
        except IntegrityError:
            db.seesion.rollback()
            flash('Catgory with the given name already Exixts')
            return redirect(url_for('edit_category',curr_login_id=curr_login_id,category_id=category.id))
        
    return render_template('edit_category.html',curr_login_id=curr_login_id,category=category)            


@app.route('/admin/<int:curr_login_id>/remove/<int:category_id>', methods=['GET', 'POST'])
def remove_category(curr_login_id, category_id):
    if not get_user_admin(curr_login_id):
        flash('You are not authorized to access this page.')
        return redirect(url_for('logout'))

    category = Category.query.get_or_404(category_id)

    if request.method == 'POST':
        db.session.delete(category)
        db.session.commit()
        return redirect(url_for('admin_dashboard', curr_login_id=curr_login_id))

    return render_template('remove_category.html', curr_login_id=curr_login_id, category=category)


     

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



if __name__=="__main__":
    app.run(port=5000,debug=True) 
