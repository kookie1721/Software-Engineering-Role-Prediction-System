from flask import Flask, render_template, url_for, request, redirect, session
import pickle
import numpy as np
import pandas as pd
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re


app = Flask(__name__)
dtc_model = pickle.load(open('final_model.pkl','rb'))
dtc_second_model = pickle.load(open('second_final_model.pkl','rb'))

app.secret_key = 'markies1'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'thesis_db'

mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            if user['userType'] == 'student':
                session['loggedin'] = True
                session['userid'] = user['id']
                session['lastName'] = user['lastName']
                session['firstName'] = user['firstName']
                session['email'] = user['email']
                session['program'] = user['program']
                mesage = 'Logged in successfully !'

                cursor.execute('SELECT * FROM predict WHERE userID = % s', (user['id'], ))
                record = cursor.fetchone()
                
                if record:
                    has_record = True
                    m_prediction = record['MAIN_ROLE']
                    s_prediction = record['SECOND_ROLE']

                    if m_prediction == 0:
                        m_prediction = 'Lead Programmer'
                    elif m_prediction == 1:
                        m_prediction = 'Project Manager'
                    elif m_prediction == 2:
                        m_prediction = 'UI/UX Designer'
                    elif m_prediction == 3:
                        m_prediction = 'Quality Assurance Engineer'
                    elif m_prediction == 4:
                        m_prediction = 'Business Analyst'
                    
                    if s_prediction == 0:
                        s_prediction = 'Lead Programmer'
                    elif s_prediction == 1:
                        s_prediction = 'Project Manager'
                    elif s_prediction == 2:
                        s_prediction = 'UI/UX Designer'
                    elif s_prediction == 3:
                        s_prediction = 'Quality Assurance Engineer'
                    elif s_prediction == 4:
                        s_prediction = 'Business Analyst'
                    elif s_prediction == 5:
                        s_prediction = 'NONE'
                else:
                    has_record = False
                return render_template('dashboard_student.html', mesage = mesage, has_record=has_record, main_role=m_prediction, second_role=s_prediction)
            elif user['userType'] == 'teacher':
                mesage = 'Teacher module is not yet implemented!!'
                return render_template('index.html', mesage = mesage) 
        else:
            mesage = 'Email or Password is incorrect!'
    return render_template('index.html', mesage = mesage)

@app.route('/dashboard_student')
def dashboard_student():
    return render_template('dashboard_student.html')

@app.route('/dashboard_student/start', methods =['GET', 'POST'])
def start():
    GPA = 0
    mesage = ''
    if request.method == 'POST'  and 'CC101' in request.form and 'CC102' in request.form  and 'ITC' in request.form  and 'IM' in request.form and 'OOP' in request.form  and 'HCI' in request.form and 'DSA' in request.form :
        CC101 = request.form['CC101']
        CC102 = request.form['CC102']
        ITC = request.form['ITC']
        IM = request.form['IM']
        OOP = request.form['OOP']
        HCI = request.form['HCI']
        DSA = request.form['DSA']

        CC101_units = (float(CC101) * 4)
        CC102_units = (float(CC102) * 4)
        ITC_units = (float(ITC) * 3)
        IM_units = (float(IM) * 4)
        OOP_units = (float(OOP) * 4)
        HCI_units = (float(HCI) * 1)
        DSA_units = (float(DSA) * 4)

        total_units = 24

        # multiplying the grades with the units of each subject and getting the sum of the multiple grades
        # to calculate the GPA.

        final_grade = (float(CC101) * 4) + (float(CC102) * 4) + (float(ITC) * 3) + (float(IM) * 4) + (float(OOP) * 4) + (float(HCI) * 1) + (float(DSA) * 4)
        

        #Dividing the final grade with the total units to generate the GPA.
        GPA = float(final_grade) / int(total_units)
        final_GPA = round(GPA, 2)

        #calculating the average grade for the programming subjects
        prog_avg = (float(CC101) + float(CC102) + float(IM) + float(OOP)) / 4
        final_prog_avg = round(prog_avg, 2)
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT program FROM users WHERE id = % s', (session['userid'],))
        program = cursor.fetchone()

        if program['program'] == 'BSIT':
            f_program = 0
        elif program['program'] == 'BSCS':
            f_program = 1

        if request.method == 'POST'  and 'CC101' in request.form and 'CC102' in request.form  and 'ITC' in request.form  and 'IM' in request.form and 'OOP' in request.form  and 'HCI' in request.form and 'DSA' in request.form:
             cursor.execute('INSERT INTO predict (userID, program, comprog1, comprog2, intro_computing, IM, OOP, HCI, DSA, comprog1_units, comprog2_units, intro_computing_units, IM_units, OOP_units, HCI_units, DSA_units, programming_avg, gpa) VALUES (% s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s )', (session['userid'], f_program, CC101, CC102, ITC, IM, OOP, HCI, DSA, CC101_units, CC102_units, ITC_units, IM_units, OOP_units, HCI_units, DSA_units, final_prog_avg, final_GPA, ))
             mysql.connection.commit()
             return render_template('result_gpa.html', GPA=final_GPA)
        else:
            mesage = 'Something went wrong!'
            return render_template('result_gpa.html', mesage=mesage)

    elif request.method == 'POST':
        mesage = 'something went wrong!'
    return render_template('start.html', mesage=mesage)


@app.route('/dashboard_student/pt', methods =['GET', 'POST'])
def pt():
    mesage = ''
    if request.method == 'POST'  and  'personality' in request.form :
        personality_type = request.form['personality']
        if personality_type == 'ENFJ':
            ENFJ = 1
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE predict SET ENFJ = % s WHERE userID = % s', (ENFJ, session['userid'], ))
            mysql.connection.commit()
            return render_template('result_pt.html', pt=personality_type)
        elif personality_type == 'ENFP':
            ENFP = 1
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE predict SET ENFP = % s WHERE userID = % s', (ENFP, session['userid'], ))
            mysql.connection.commit()
            return render_template('result_pt.html', pt=personality_type)
        elif personality_type == 'ENTJ':
            ENTJ = 1
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE predict SET ENTJ = % s WHERE userID = % s', (ENTJ, session['userid'], ))
            mysql.connection.commit()
            return render_template('result_pt.html', pt=personality_type)
        elif personality_type == 'ENTP':
            ENTP = 1
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE predict SET ENTP = % s WHERE userID = % s', (ENTP, session['userid'], ))
            mysql.connection.commit()
            return render_template('result_pt.html', pt=personality_type)
        elif personality_type == 'ESFJ':
            ESFJ = 1
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE predict SET ESFJ = % s WHERE userID = % s', (ESFJ, session['userid'], ))
            mysql.connection.commit()
            return render_template('result_pt.html', pt=personality_type)
        elif personality_type == 'ESFP':
            ESFP = 1
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE predict SET ESFP = % s WHERE userID = % s', (ESFP, session['userid'], ))
            mysql.connection.commit()
            return render_template('result_pt.html', pt=personality_type)
        elif personality_type == 'ESTJ':
            ESTJ = 1
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE predict SET ESTJ = % s WHERE userID = % s', (ESTJ, session['userid'], ))
            mysql.connection.commit()
            return render_template('result_pt.html', pt=personality_type)
        elif personality_type == 'ESTP':
            ESTP = 1
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE predict SET ESTP = % s WHERE userID = % s', (ESTP, session['userid'], ))
            mysql.connection.commit()
            return render_template('result_pt.html', pt=personality_type)
        elif personality_type == 'INFJ':
            INFJ = 1
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE predict SET INFJ = % s WHERE userID = % s', (INFJ, session['userid'], ))
            mysql.connection.commit()
            return render_template('result_pt.html', pt=personality_type)
        elif personality_type == 'INFP':
            INFP = 1
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE predict SET INFP = % s WHERE userID = % s', (INFP, session['userid'], ))
            mysql.connection.commit()
            return render_template('result_pt.html', pt=personality_type)
        elif personality_type == 'INTJ':
            INTJ = 1
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE predict SET INTJ = % s WHERE userID = % s', (INTJ, session['userid'], ))
            mysql.connection.commit()
            return render_template('result_pt.html', pt=personality_type)
        elif personality_type == 'INFP':
            INFP = 1
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE predict SET INFP = % s WHERE userID = % s', (INFP, session['userid'], ))
            mysql.connection.commit()
            return render_template('result_pt.html', pt=personality_type)
        elif personality_type == 'ISFJ':
            ISFJ = 1
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE predict SET ISFJ = % s WHERE userID = % s', (ISFJ, session['userid'], ))
            mysql.connection.commit()
            return render_template('result_pt.html', pt=personality_type)
        elif personality_type == 'ISFP':
            ISFP = 1
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE predict SET ISFP = % s WHERE userID = % s', (ISFP, session['userid'], ))
            mysql.connection.commit()
            return render_template('result_pt.html', pt=personality_type)
        elif personality_type == 'ISTJ':
            ISTJ = 1
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE predict SET ISTJ = % s WHERE userID = % s', (ISTJ, session['userid'], ))
            mysql.connection.commit()
            return render_template('result_pt.html', pt=personality_type)
        elif personality_type == 'ISTP':
            ISTP = 1
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE predict SET ISTP = % s WHERE userID = % s', (ISTP, session['userid'], ))
            mysql.connection.commit()
            return render_template('result_pt.html', pt=personality_type)
        else:
             mesage = 'something went wrong!'
             return render_template('result_pt.html', mesage = mesage)
    
    elif request.method == 'POST':
        mesage = 'something went wrong!'
    return render_template('pt.html', mesage = mesage)


@app.route('/dashboard_student/mt', methods =['GET', 'POST'])
def mt():
    mesage = ''
    if request.method == 'POST'  and  'mul_int' in request.form :
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.form.getlist('mul_int'):
            MI_list = request.form.getlist('mul_int')
            if 'existential' in MI_list:  
                cursor.execute('UPDATE predict SET EXISTENTIAL = % s WHERE userID = % s', (1, session['userid'], ))
                mysql.connection.commit()
            if 'interpersonal' in MI_list:  
                cursor.execute('UPDATE predict SET INTERPERSONAL = % s WHERE userID = % s', (1, session['userid'], ))
                mysql.connection.commit()
            if 'intrapersonal' in MI_list:  
                cursor.execute('UPDATE predict SET INTRAPERSONAL = % s WHERE userID = % s', (1, session['userid'], ))
                mysql.connection.commit()
            if 'kinesthetic' in MI_list:  
                cursor.execute('UPDATE predict SET KINESTHETIC = % s WHERE userID = % s', (1, session['userid'], ))
                mysql.connection.commit()
            if 'logical' in MI_list:  
                cursor.execute('UPDATE predict SET LOGICAL = % s WHERE userID = % s', (1, session['userid'], ))
                mysql.connection.commit()
                
            if 'musical' in MI_list:  
                cursor.execute('UPDATE predict SET MUSICAL = % s WHERE userID = % s', (1, session['userid'], ))
                mysql.connection.commit()
            if 'naturalistic' in MI_list:  
                cursor.execute('UPDATE predict SET NATURALISTIC = % s WHERE userID = % s', (1, session['userid'], ))
                mysql.connection.commit()
            if 'verbal' in MI_list:  
                cursor.execute('UPDATE predict SET VERBAL = % s WHERE userID = % s', (1, session['userid'], ))
                mysql.connection.commit()
            if 'visual' in MI_list:  
                cursor.execute('UPDATE predict SET VISUAL = % s WHERE userID = % s', (1, session['userid'], ))
                mysql.connection.commit()
            return render_template('result_mt.html', mi_li=MI_list)
    elif request.method == 'POST':
        mesage = 'Select at least one multiple intelligence!!'
    return render_template('mt.html', mesage=mesage)


#predict page
@app.route('/dashboard_student/predict')
def predict():
    return render_template('predict.html')

#result page
@app.route('/dashboard_student/result_predict', methods =['GET', 'POST'])
def result_predict():
    newdata=dict()
    m_prediction = 0
    s_prediction = 0
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM predict WHERE userID = % s', (session['userid'], ))
    predict_user = cursor.fetchone()
    if predict_user:
        newdata['Program']= predict_user['program']
        newdata['COMPROG 1']= predict_user['comprog1']
        newdata['COMPROG 2']= predict_user['comprog2']
        newdata['INTRO TO COMPUTING']= predict_user['intro_computing']
        newdata['INFO MANAGEMENT']= predict_user['IM']
        newdata['OOP']= predict_user['OOP']
        newdata['HCI']= predict_user['HCI']
        newdata['DATA STRUCTURES AND ALGO']= predict_user['DSA']

        newdata['COMPROG1_4_units']= predict_user['comprog1_units']
        newdata['COMPROG2_4_units']= predict_user['comprog2_units']
        newdata['INTRO_TO_COMPUTING_3_units']= predict_user['intro_computing_units']
        newdata['INFO_MANAGEMENT_4_units']= predict_user['IM_units']
        newdata['OOP_4_units']= predict_user['OOP_units']
        newdata['HCI_1_units']= predict_user['HCI_units']
        newdata['DATA STRUCTURES_AND_ALGO_4_units']= predict_user['DSA_units']

        newdata['Programming_AVG']= predict_user['programming_avg']
        newdata['GPA']= predict_user['gpa']

        newdata['ENFJ']= predict_user['ENFJ']
        newdata['ENFP']= predict_user['ENFP']
        newdata['ENTJ']= predict_user['ENTJ']
        newdata['ENTP']= predict_user['ENTP']
        newdata['ESFJ']= predict_user['ESFJ']
        newdata['ESFP']= predict_user['ESFP']
        newdata['ESTJ']= predict_user['ESTJ']
        newdata['ESTP']= predict_user['ESTP']
        newdata['INFJ']= predict_user['INFJ']
        newdata['INFP']= predict_user['INFP']
        newdata['INTJ']= predict_user['INTJ']
        newdata['INTP']= predict_user['INTP']
        newdata['ISFJ']= predict_user['ISFJ']
        newdata['ISFP']= predict_user['ISFP']
        newdata['ISTJ']= predict_user['ISTJ']
        newdata['ISTP']= predict_user['ISTP']

        newdata['EXISTENTIAL']= predict_user['EXISTENTIAL']
        newdata['INTERPERSONAL']= predict_user['INTERPERSONAL']
        newdata['INTRAPERSONAL']= predict_user['INTRAPERSONAL']
        newdata['KINESTHETIC']= predict_user['KINESTHETIC']
        newdata['LOGICAL']= predict_user['LOGICAL']
        newdata['MUSICAL']= predict_user['MUSICAL']
        newdata['NATURALISTIC']= predict_user['NATURALISTIC']
        newdata['VERBAL']= predict_user['VERBAL']
        newdata['VISUAL']= predict_user['VISUAL']

        df=pd.DataFrame([newdata.values()],columns=list(newdata.keys()))
        
        m_prediction=dtc_model.predict(df)
        
        s_prediction=dtc_second_model.predict(df)
        
        cursor.execute('UPDATE predict SET MAIN_ROLE = % s, SECOND_ROLE = % s WHERE userID = % s', (int(m_prediction), int(s_prediction), predict_user['userID'], ))
        mysql.connection.commit()

        if m_prediction == 0:
            m_prediction = 'Lead Programmer'
        elif m_prediction == 1:
            m_prediction = 'Project Manager'
        elif m_prediction == 2:
            m_prediction = 'UI/UX Designer'
        elif m_prediction == 3:
            m_prediction = 'Quality Assurance Engineer'
        elif m_prediction == 4:
            m_prediction = 'Business Analyst'
        
        if s_prediction == 0:
            s_prediction = 'Lead Programmer'
        elif s_prediction == 1:
            s_prediction = 'Project Manager'
        elif s_prediction == 2:
            s_prediction = 'UI/UX Designer'
        elif s_prediction == 3:
            s_prediction = 'Quality Assurance Engineer'
        elif s_prediction == 4:
            s_prediction = 'Business Analyst'
        elif s_prediction == 5:
            s_prediction = 'NONE'
        
        cursor.execute('SELECT * FROM predict WHERE userID = % s', (predict_user['userID'], ))
        record = cursor.fetchone()
        if record:
            session['has_record'] = True
        else:
            session['has_record'] = False

        print('\n\nMain Role Prediction: ',m_prediction,'\n\n')
        print('\n\nSecond Role Prediction: ',s_prediction,'\n\n')

    return render_template('result_predict.html', m_prediction = m_prediction, s_prediction = s_prediction)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('firstName', None)
    session.pop('lastName', None)
    session.pop('email', None)
    session.pop('has_record', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST'  and 'userType' in request.form and 'firstName' in request.form  and 'lastName' in request.form  and 'password' in request.form and 'email' in request.form and 'program' in request.form  and 'section' in request.form :
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        password = request.form['password']
        email = request.form['email']
        userType = request.form['userType']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = % s', (email,))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not firstName or not lastName or not userType or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO users (userType, firstName, lastName, email, password, section, program) VALUES (% s, % s, % s, % s, % s, % s, % s)', (userType, firstName, lastName, email, password, session['section'], session['program'],))
            mysql.connection.commit()
            mesage = 'You have successfully registered!'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage = mesage)


if __name__ == "__main__":
    app.run(debug=True)

