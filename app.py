from flask import Flask, render_template, request, url_for, redirect , flash  , session  , abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash , check_password_hash 
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
import os
from flask_login import current_user ,login_manager , LoginManager , login_user , UserMixin , logout_user , login_required
from functools import wraps
import os
from sqlalchemy.dialects.postgresql import psycopg2 

app = Flask(__name__)
login_manager = LoginManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://pfnafjzkikythh:33f0a7f09ddb70a1bace9cce316108f81e0997bc9b2e3ee3d3f45b0b9bb9b140@ec2-54-156-8-21.compute-1.amazonaws.com:5432/d84phsc71dtl3'
db = SQLAlchemy(app)

app.secret_key = os.urandom(24)
login_manager.login_view = 'login'
login_manager.init_app(app)
app.config['REMEMBER_COOKIE_SECURE'] = True

if 'DYNO' in os.environ:  # Kiểm tra môi trường Heroku
    app.config['REMEMBER_COOKIE_SECURE'] = True
else:
    app.config['REMEMBER_COOKIE_SECURE'] = False

#-------------------------------------------------------------------------------------------------  

@login_manager.user_loader
def load_user(user_id):
    if user_id > -1:
        user = User.query.get(user_id)
        if user and user.is_student:
            return user
    else:
        admin = admin_user.query.get(abs(user_id))
        if admin and admin.is_admin:
            return admin
    

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and  current_user.is_admin:
            return f(*args, **kwargs)
        else:
            return render_template('login.html')
    return decorated_function
#-------------------------------------------------------------------------------------------------  

class admin_user(db.Model):
    id = db.Column(db.Integer , primary_key = True ,autoincrement = True)
    admin_username = db.Column(db.String , nullable = False)
    ad_username = db.Column(db.String() , nullable = False)
    password_hash = db.Column(db.String() , nullable  = False)
    is_admin = db.Column(db.Boolean, default=True) 
    is_student = db.Column(db.Boolean , default = False)    

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def get_id(self):
        return -self.id
    def is_active(self):
        return True
    def is_authenticated(self):
        return True
    
class User(db.Model , UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(), nullable=False)
    password_hash = db.Column(db.String(), nullable=False)
    student = db.relationship('Student', backref=db.backref('user', uselist=False)) 
    is_student = db.Column(db.Boolean , default = True)
    is_admin = db.Column(db.Boolean, default=False ) 
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def get_id(self):
        return self.id
    def is_active(self):
        return True
    
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(), nullable=False)
    Date_of_birth = db.Column(db.Date, nullable=False)
    Gender = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer , nullable = False)
    Nationality = db.Column(db.String, nullable=False)
    Address = db.Column(db.String, nullable=False)
    Phone_number = db.Column(db.Integer, nullable=False)
    Email = db.Column(db.String)
    Class = db.Column(db.String, nullable=False)
    student_activity = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#-------------------------------------------------------------------------------------------------  

#-------------------------------------------------------------------------------------------------  

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Kiểm tra người dùng là admin_user hay User
        user = User.query.filter_by(username=username).first()
        admin = admin_user.query.filter_by(ad_username=username).first()
        if user and user.check_password(password):
            login_user(user)
            session['user'] = user.id
            current_user = user
            print("h")
            print(current_user.id)
            print(current_user.is_student)
            print("h")
           
            return redirect(url_for('student_detail', id=user.id))
        elif admin and admin.check_password(password):
            login_user(admin)
            
            session['admin'] = admin.id
            current_user = admin
            print(current_user.is_admin)

            return redirect(url_for('students'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')
#-------------------------------------------------------------------------------------------------  

@app.route('/signup' , methods  = ['GET' , 'POST'])
def signup():
    existing_user = admin_user.query.all()
    if not  existing_user:
        if request.method == 'POST':
            admin_username = request.form['yourname']
            username = request.form['username'] 
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            if password == confirm_password:
                new_user = admin_user(admin_username = admin_username ,ad_username = username )
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                return   redirect(url_for('login'))
            else:
                return flash('something wrong')
        else:
            return render_template('signup.html')
    else:
       return render_template('login.html')

#-------------------------------------------------------------------------------------------------  

@app.route('/')
def home():
    return redirect(url_for('login'))
#-------------------------------------------------------------------------------------------------  
@app.route('/add', methods=['GET' ,  'POST'])
@admin_required
def add_student():
    print(current_user.is_admin)
    if request.method == 'POST':
        Name = request.form['name']
        Date_of_birth = request.form['birthday']
        Date_of_birth = datetime.strptime(Date_of_birth, '%Y-%m-%d').date()
        today = datetime.now().date().year
        age = today  - Date_of_birth.year 
        Gender = request.form['Gender']
        Nationality = request.form['nationality']
        Address = request.form['address']
        Phone_number = request.form['phonenumber']
        Email = request.form['email']
        Class = request.form['Class']
        username = request.form['username']
        password = request.form['password']       
        try:
            valid_email = validate_email(Email)
            # Tạo người dùng mới
            user = User(username=username)
            user.set_password(password)
            # Tạo học sinh mới và liên kết với người dùng
            student = Student(Name=Name, Date_of_birth=Date_of_birth, Gender=Gender,age  = age, Nationality=Nationality,
                              Address=Address, Phone_number=Phone_number, Email=valid_email.email, Class=Class, user=user)
            db.session.add(user)
            db.session.add(student)
            db.session.commit()
            return redirect(url_for('students'))
        except EmailNotValidError:
            return 'Invalid email address!'       
    else:
        return render_template('add.html')
#-------------------------------------------------------------------------------------------------  

@app.route('/students/<int:id>/update' , methods = ['GET' , 'POST'])
@admin_required
def update_student(id):
    print(current_user.is_admin) 
    student = Student.query.get(id)
    if request.method == 'POST':
        student.Name  = request.form['Name']
        student.birthday  = request.form['BirthDay']
        student.Gender  = request.form['Gender']
        student.Nationality  = request.form['Nationality']
        student.Address  = request.form['Address']
        student.Phone_number  = request.form['Phone_number']
        student.Email  = request.form['Email']
        student.Class  = request.form['Class']
        db.session.commit()
        return redirect(url_for('students'))
    else:
        return render_template('update.html', student=student)
    
#-------------------------------------------------------------------------------------------------  

@app.route('/logout' , methods = ['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))   
#-------------------------------------------------------------------------------------------------  

@app.route('/students/<int:id>/delete', methods=['POST' , 'GET'])
@admin_required
def delete_student(id):
    student = Student.query.get(id)
    user = student.user
    db.session.delete(student)
    db.session.delete(user)  # Xóa cả bản ghi người dùng
    db.session.commit()
    return redirect(url_for('students'))
#-------------------------------------------------------------------------------------------------  
@app.route('/students')
@login_required
def students():
    students = Student.query.all()
    return render_template('students.html', students=students)
#-------------------------------------------------------------------------------------------------  

@app.route('/students/<int:id>')
@login_required
def student_detail(id):
    student = Student.query.get(id)

    if 'current_user' in session:
        current_user = session['current_user']

        if current_user.is_authenticated:
            if current_user.is_admin:
                return render_template('student_detail.html', student=student, current_user=current_user)
    return render_template('student_detail.html', student=student)
#-------------------------------------------------------------------------------------------------  

@app.route('/update_activity/<int:id>', methods=['POST', 'GET'])
@login_required
def update_activity(id):
    print(current_user.is_admin)

    stu = Student.query.get(id)
    if request.method == 'POST':
        new_activity = request.form['activity']
        if current_user.is_admin == True: 
            if stu.student_activity:
                stu.student_activity = stu.student_activity + '\n' + current_user.admin_username  + ': ' + new_activity
            else:
                stu.student_activity = current_user.admin_username + ': ' + new_activity
        else:          
            if stu.student_activity:
                stu.student_activity = stu.student_activity + '\n' + stu.Name + ': ' + new_activity
            else:
                stu.student_activity = stu.Name + ':' + new_activity
        db.session.commit()
        return render_template('student_detail.html', student=stu)
    
    return redirect(url_for('student_detail.html'))
#-------------------------------------------------------------------------------------------------  


if __name__ == '__main__':
        app.run(debug=True)
