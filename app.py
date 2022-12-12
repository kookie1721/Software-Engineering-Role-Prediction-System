from flask import Flask, flash, render_template, url_for, request, redirect, session
import pickle
import numpy as np
import pandas as pd
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import datetime


app = Flask(__name__)
dtc_model = pickle.load(open('main_final_model.pkl','rb'))
dtc_second_model = pickle.load(open('second_final_model.pkl','rb'))

app.secret_key = 'markies1'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'thesis_db'

mysql = MySQL(app)

@app.route('/')
@app.route('/Home', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:

        session['email'] = request.form['email']
        session['password'] = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        user_record = cursor.execute('SELECT * FROM users WHERE email = % s AND password = % s', (session['email'], session['password'], ))
        user = cursor.fetchone()

        registered_studs_result = cursor.execute('SELECT * FROM users')
        registered_studs_data = cursor.fetchall()

        registered_studs_result_10 = cursor.execute('SELECT * FROM users ORDER BY id DESC LIMIT 10')
        registered_studs_data_10 = cursor.fetchall()

        session['no_registered_studs_result'] = registered_studs_result
        session['no_registered_studs_data_10'] = registered_studs_data_10

        predicted_studs_result_IT = cursor.execute('SELECT predict.*, users.AY, users.firstName, users.lastName, users.section, users.program FROM predict INNER JOIN users ON users.id = predict.userID WHERE predict.program = 0')
        predicted_studs_data_IT = cursor.fetchall()
        session['no_predicted_studs_result_IT'] = predicted_studs_result_IT
        session['no_predicted_studs_data_IT'] = predicted_studs_data_IT

        predicted_studs_result_CS = cursor.execute('SELECT predict.*, users.AY, users.firstName, users.lastName, users.section, users.program FROM predict INNER JOIN users ON users.id = predict.userID  WHERE predict.program = 1')
        predicted_studs_data_CS = cursor.fetchall()
        session['no_predicted_studs_result_CS'] = predicted_studs_result_CS
        session['no_predicted_studs_data_CS'] = predicted_studs_data_CS

        predicted_studs_result_10_IT = cursor.execute('SELECT predict.*, users.AY, users.firstName, users.lastName, users.section, users.program FROM predict INNER JOIN users ON users.id = predict.userID WHERE predict.program = 0 ORDER BY predict.id DESC LIMIT 10')
        predicted_studs_data_10_IT = cursor.fetchall()
        session['no_predicted_studs_result_10_IT'] = predicted_studs_result_10_IT
        session['no_predicted_studs_data_10_IT'] = predicted_studs_data_10_IT

        predicted_studs_result_10_CS = cursor.execute('SELECT predict.*, users.AY, users.firstName, users.lastName, users.section, users.program FROM predict INNER JOIN users ON users.id = predict.userID WHERE predict.program = 1 ORDER BY predict.id DESC LIMIT 10')
        predicted_studs_data_10_CS = cursor.fetchall()
        session['no_predicted_studs_result_10_CS'] = predicted_studs_result_10_CS
        session['no_predicted_studs_data_10_CS'] = predicted_studs_data_10_CS

        if user_record == 1:
            if user['userType'] == 'student':
                session['loggedin'] = True
                loggedin = True
                session['userid'] = user['id']
                session['lastName'] = user['lastName']
                session['firstName'] = user['firstName']
                session['email'] = user['email']
                session['program'] = user['program']
                session['section'] = user['section']
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
                    return render_template('dashboard_student.html', loggedin=loggedin, mesage = mesage, has_record=has_record, main_role=m_prediction, second_role=s_prediction)
                else:
                    has_record = False
                    return render_template('dashboard_student.html', loggedin=loggedin, mesage = mesage, has_record=has_record)
            elif user['userType'] == 'teacher':
                no = 0   
                session['loggedin'] = True
                loggedin = True
                session['userid'] = user['id']
                session['lastName'] = user['lastName']
                session['firstName'] = user['firstName']
                session['email'] = user['email']
                session['program'] = user['program']
                mesage = 'Logged in successfully !'

                return render_template('dashboard_teacher.html', loggedin=loggedin, mesage = mesage) 
        else:
            mesage = 'Email or Password is incorrect!'
    return render_template('index.html', mesage = mesage)

@app.route('/dashboard_student/profile')
def view_profile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = % s', (session['userid'],))
    user = cursor.fetchone()

    session['loggedin'] = True
    loggedin = True
    session['userid'] = user['id']
    session['lastName'] = user['lastName']
    session['firstName'] = user['firstName']
    session['email'] = user['email']
    session['program'] = user['program']
    session['section'] = user['section']

    is_predict = cursor.execute('SELECT * FROM predict WHERE predict.userID = % s', (session['userid'], ))
    user_roles = cursor.fetchone()

    return render_template('view_profile.html', user_roles=user_roles, is_predict=is_predict)

@app.route('/student_records/student_profile', methods=['GET', 'POST'])
def view_student():
    if request.method == 'POST'  and 's_record' in request.form and 'userID' in request.form:
        userID = request.form['userID'] 
        student_records_page = request.form['s_record']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE id = % s', (userID,))
        user = cursor.fetchone()

        session['loggedin'] = True
        loggedin = True
        session['userid'] = user['id']
        session['lastName'] = user['lastName']
        session['firstName'] = user['firstName']
        session['email'] = user['email']
        session['program'] = user['program']
        session['section'] = user['section']

        is_predict = cursor.execute('SELECT * FROM predict WHERE predict.userID = % s', (session['userid'], ))
        user_roles = cursor.fetchone()

        return render_template('view_student.html', student_records_page=student_records_page, user_roles=user_roles, is_predict=is_predict)

    return render_template('view_student.html', student_records_page=student_records_page, user_roles=user_roles, is_predict=is_predict)

@app.route('/groupings_CS/student_profile', methods=['GET', 'POST'])
def view_student_CS():
    if request.method == 'POST'  and 'g_cs' in request.form and 'userID' in request.form:
        userID = request.form['userID'] 
        groupings_cs_page = request.form['g_cs']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE id = % s', (userID,))
        user = cursor.fetchone()

        session['loggedin'] = True
        loggedin = True
        session['userid'] = user['id']
        session['lastName'] = user['lastName']
        session['firstName'] = user['firstName']
        session['email'] = user['email']
        session['program'] = user['program']
        session['section'] = user['section']

        is_predict = cursor.execute('SELECT * FROM predict WHERE predict.userID = % s', (session['userid'], ))
        user_roles = cursor.fetchone()

        return render_template('view_student.html', groupings_cs_page=groupings_cs_page, user_roles=user_roles, is_predict=is_predict)

    return render_template('view_student.html', groupings_cs_page=groupings_cs_page, user_roles=user_roles, is_predict=is_predict)

@app.route('/groupings_IT/student_profile', methods=['GET', 'POST'])
def view_student_IT():
    if request.method == 'POST'  and 'g_it' in request.form and 'userID' in request.form:
        userID = request.form['userID'] 
        groupings_it_page = request.form['g_it']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE id = % s', (userID,))
        user = cursor.fetchone()

        session['loggedin'] = True
        loggedin = True
        session['userid'] = user['id']
        session['lastName'] = user['lastName']
        session['firstName'] = user['firstName']
        session['email'] = user['email']
        session['program'] = user['program']
        session['section'] = user['section']

        is_predict = cursor.execute('SELECT * FROM predict WHERE predict.userID = % s', (session['userid'], ))
        user_roles = cursor.fetchone()

        return render_template('view_student.html', groupings_it_page=groupings_it_page, user_roles=user_roles, is_predict=is_predict)

    return render_template('view_student.html', groupings_it_page=groupings_it_page, user_roles=user_roles, is_predict=is_predict)

@app.route('/dashboard_student/edit_profile', methods =['GET', 'POST'])
def edit_profile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = % s', (session['userid'], ))
    user = cursor.fetchone()

    session['loggedin'] = True
    loggedin = True
    session['userid'] = user['id']
    session['lastName'] = user['lastName']
    session['firstName'] = user['firstName']
    session['email'] = user['email']
    session['program'] = user['program']
    session['section'] = user['section']
    is_predict = cursor.execute('SELECT * FROM predict WHERE predict.userID = % s', (session['userid'], ))
    user_roles = cursor.fetchone()
    
    if request.method == 'POST'  and 'firstName' in request.form and 'lastName' in request.form and 'email' in request.form and 'program' in request.form and 'section' in request.form: 
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['email']
        program = request.form['program']
        section = request.form['section']
        cursor.execute('UPDATE users SET firstName = % s, lastName = % s, email = % s, program = % s, section = % s WHERE id = % s ', (firstName, lastName, email, program, section, session['userid'], ))
        mysql.connection.commit()

        flash("Basic information was edited successfully.")
        mes = "Information was edited successfully."
        return redirect(url_for('view_profile'))

    return render_template('edit_profile.html', user_roles=user_roles, is_predict=is_predict)

@app.route('/dashboard_student')
def dashboard_student():

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = % s', (session['userid'], ))
    user = cursor.fetchone()
    session['loggedin'] = True
    loggedin = True
    session['userid'] = user['id']
    session['lastName'] = user['lastName']
    session['firstName'] = user['firstName']
    session['email'] = user['email']
    session['program'] = user['program']

    cursor.execute('SELECT * FROM predict WHERE userID = % s', (session['userid'], ))
    record = cursor.fetchone()
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
    
    if record:
        has_record = True
        return render_template('dashboard_student.html', has_record=has_record, main_role=m_prediction, second_role = s_prediction)

    return render_template('dashboard_student.html', main_role=m_prediction, second_role = s_prediction)

@app.route('/dashboard_student_no_roles')
def dashboard_student_no_roles():
    return render_template('dashboard_student.html')
    

@app.route('/dashboard_student/start_repredict')
def repredict():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT predict.id, users.firstName, users.lastName FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.userID = % s', (session['userid'],))
    del_user = cursor.fetchone()

    cursor.execute('DELETE FROM predict WHERE id = % s', (del_user['id'], ))
    mysql.connection.commit()

    return redirect(url_for('start'))

@app.route('/dashboard_student/start', methods =['GET', 'POST'])
def start():
    GPA = 0
    mesage = ''
    userID = session['userid']
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
        cursor.execute('SELECT program FROM users WHERE id = % s', (userID,))
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
        elif personality_type == 'INTP':
            INTP = 1
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE predict SET INTP = % s WHERE userID = % s', (INTP, session['userid'], ))
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
        
        s_prediction=dtc_second_model.predict(df)
        m_prediction=dtc_model.predict(df)
        
       
        
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
            session['main_role'] = m_prediction
            session['second_role'] = s_prediction
        else:
            session['has_record'] = False

        print('\n\nMain Role Prediction: ',m_prediction,'\n\n')
        print('\n\nSecond Role Prediction: ',s_prediction,'\n\n')

    return render_template('result_predict.html', m_prediction = m_prediction, s_prediction = s_prediction)

@app.route('/dashboard_teacher')
def dashboard_teacher():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        registered_studs_result = cursor.execute('SELECT * FROM users')
        registered_studs_data = cursor.fetchall()

        registered_studs_result_10 = cursor.execute('SELECT * FROM users ORDER BY id DESC LIMIT 10')
        registered_studs_data_10 = cursor.fetchall()

        session['no_registered_studs_result'] = registered_studs_result
        session['no_registered_studs_data_10'] = registered_studs_data_10

        predicted_studs_result_IT = cursor.execute('SELECT predict.*, users.AY, users.firstName, users.lastName, users.section, users.program FROM predict INNER JOIN users ON users.id = predict.userID WHERE predict.program = 0')
        predicted_studs_data_IT = cursor.fetchall()
        session['no_predicted_studs_result_IT'] = predicted_studs_result_IT
        session['no_predicted_studs_data_IT'] = predicted_studs_data_IT

        predicted_studs_result_CS = cursor.execute('SELECT predict.*, users.AY, users.firstName, users.lastName, users.section, users.program FROM predict INNER JOIN users ON users.id = predict.userID  WHERE predict.program = 1')
        predicted_studs_data_CS = cursor.fetchall()
        session['no_predicted_studs_result_CS'] = predicted_studs_result_CS
        session['no_predicted_studs_data_CS'] = predicted_studs_data_CS

        predicted_studs_result_10_IT = cursor.execute('SELECT predict.*, users.AY, users.firstName, users.lastName, users.section, users.program FROM predict INNER JOIN users ON users.id = predict.userID WHERE predict.program = 0 ORDER BY predict.id DESC LIMIT 10')
        predicted_studs_data_10_IT = cursor.fetchall()
        session['no_predicted_studs_result_10_IT'] = predicted_studs_result_10_IT
        session['no_predicted_studs_data_10_IT'] = predicted_studs_data_10_IT

        predicted_studs_result_10_CS = cursor.execute('SELECT predict.*, users.AY, users.firstName, users.lastName, users.section, users.program FROM predict INNER JOIN users ON users.id = predict.userID WHERE predict.program = 1 ORDER BY predict.id DESC LIMIT 10')
        predicted_studs_data_10_CS = cursor.fetchall()
        session['no_predicted_studs_result_10_CS'] = predicted_studs_result_10_CS
        session['no_predicted_studs_data_10_CS'] = predicted_studs_data_10_CS

        return render_template('dashboard_teacher.html')



#groupings module BSCS
@app.route('/groupings_CS', methods =['GET', 'POST'])
def groupings_CS():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sections_CS = cursor.execute("SELECT DISTINCT users.section, predict.program FROM users INNER JOIN predict ON users.id = predict.userID WHERE users.program = 'BSCS';")
    sections_CS = cursor.fetchall()

    result1 = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' ORDER BY predict.id DESC")
    students_BSCS3A = cursor.fetchall()

    result2 = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' ORDER BY predict.id DESC")
    students_BSCS3B = cursor.fetchall()

    result3 = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' ORDER BY predict.id DESC")
    students_BSCS3C = cursor.fetchall()

    result4 = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '1' and users.section = '3D' ORDER BY predict.id DESC")
    students_BSCS3D = cursor.fetchall()

    result1_wo = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.id DESC")
    students_BSCS3A_wo = cursor.fetchall()

    result2_wo = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.id DESC")
    students_BSCS3B_wo = cursor.fetchall()

    result3_wo = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.id DESC")
    students_BSCS3C_wo = cursor.fetchall()

    result4_wo = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '1' and users.section = '3D' and predict._group = 'none' ORDER BY predict.id DESC")
    students_BSCS3D_wo = cursor.fetchall()

    result9 = cursor.execute("SELECT users.id, users.AY, users.firstName, users.lastName, users.section, users.program, predict._group, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '1' ORDER BY predict.id DESC")
    students_all = cursor.fetchall()

    result10 = cursor.execute("SELECT users.AY, users.firstName, users.lastName, users.section, users.program, predict._group, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '1' and predict._group = 'none' ORDER BY predict.id DESC")
    students_wo_group = cursor.fetchall()
    if request.method == 'POST'  and 'program' in request.form and 'section' in request.form:
        group_size = int(request.form['s_groupSize'])
        program = request.form['program']
        section = request.form['section']

        if program == 'BSCS' and section == '3A':

            if result1 == 0:
                mes_no_studs = "There are no students in this program and section (BSCS-3A) or they might not have predicted their main and secondary roles yet!"
                return render_template('groupings_CS.html', result1_wo=result1_wo, students_wo_group = students_wo_group, mes_no_studs=mes_no_studs, students_all = students_all, students_BSCS3A = len(students_BSCS3A), students_BSCS3B = len(students_BSCS3B), students_BSCS3C = len(students_BSCS3C), students_BSCS3D = len(students_BSCS3D), sections_CS=sections_CS)

            result_check = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.id DESC")
            students_BSCS3A_check = cursor.fetchall()

            if result_check == 0:
                mes_no_studs = "Students in this program and section have already been grouped."
                return render_template('groupings_CS.html', result1_wo=result1_wo, students_wo_group=students_wo_group, mes_no_studs=mes_no_studs, students_all = students_all, students_BSCS3A = len(students_BSCS3A), students_BSCS3B = len(students_BSCS3B), students_BSCS3C = len(students_BSCS3C), students_BSCS3D = len(students_BSCS3D), sections_CS=sections_CS)
            else:
                if group_size == 3:
                    no_of_groups = round(int(len(students_BSCS3A)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()
                            

                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSCS3A) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result3_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student3_remain = cursor.fetchone()

                                    if student3_remain:
                                        student3_remain_id = student3_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_remain_id)))        
                                        mysql.connection.commit()

                                    remain_students = remain_students - 1

                                                
                                no_of_groups = no_of_groups - 1
                            
                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1

                    mes_s = "Students were successfully formed with 3 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_CS.html', result1_wo=result1_wo, mes_s=mes_s, mes=mes, students_all = students_all, students_BSCS3A = len(students_BSCS3A), students_BSCS3B = len(students_BSCS3B), students_BSCS3C = len(students_BSCS3C), students_BSCS3D = len(students_BSCS3D), sections_CS=sections_CS)
                #When the selected group size is 4
                elif group_size == 4:
                    no_of_groups = round(int(len(students_BSCS3A)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result4_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '3' and predict._group = 'none'")
                    student_QA_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    result4_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '3' and predict._group = 'none'")
                    student_QA_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups and result4_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()

                            result4 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA = cursor.fetchone()
                            

                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA:
                                student_QA_id = student_QA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups and result4_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()

                            result4_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA_s:
                                student_QA_id_s = student_QA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSCS3A) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result4_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student4_remain = cursor.fetchone()

                                    if student4_remain:
                                        student4_remain_id = student4_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_remain_id)))        
                                        mysql.connection.commit()

                                    remain_students = remain_students - 1

                                                
                                no_of_groups = no_of_groups - 1
                            
                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1
                    mes_s = "Students were successfully formed with 4 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_CS.html', result1_wo=result1_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSCS3A = len(students_BSCS3A), students_BSCS3B = len(students_BSCS3B), students_BSCS3C = len(students_BSCS3C), students_BSCS3D = len(students_BSCS3D), sections_CS=sections_CS)

                #When the selected group size is 5
                elif group_size == 5:
                    no_of_groups = round(int(len(students_BSCS3A)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result4_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '3' and predict._group = 'none'")
                    student_QA_a = cursor.fetchall()

                    result5_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '4' and predict._group = 'none'")
                    student_BA_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    result4_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '3' and predict._group = 'none'")
                    student_QA_s_a = cursor.fetchall()

                    result5_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '4' and predict._group = 'none'")
                    student_BA_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups and result4_a >= no_of_groups and result5_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()

                            result4 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA = cursor.fetchone()

                            result5 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA:
                                student_QA_id = student_QA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA:
                                student_BA_id = student_BA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups and result4_s_a >= no_of_groups and result5_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()

                            result4_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA_s = cursor.fetchone()

                            result5_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA_s:
                                student_QA_id_s = student_QA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA_s:
                                student_BA_id_s = student_BA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSCS3A) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result5_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student5_remain = cursor.fetchone()

                                    if student5_remain:
                                        student5_remain_id = student5_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student5_remain_id)))        
                                        mysql.connection.commit()

                                    remain_students = remain_students - 1
                                                
                                no_of_groups = no_of_groups - 1
                            
                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1
                    mes_s = "Students were successfully formed with 5 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_CS.html', result1_wo=result1_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSCS3A = len(students_BSCS3A), students_BSCS3B = len(students_BSCS3B), students_BSCS3C = len(students_BSCS3C), students_BSCS3D = len(students_BSCS3D), sections_CS=sections_CS)
                #When the selected group size is 6
                elif group_size == 6:
                    no_of_groups = round(int(len(students_BSCS3A)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result4_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '3' and predict._group = 'none'")
                    student_QA_a = cursor.fetchall()

                    result5_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '4' and predict._group = 'none'")
                    student_BA_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    result4_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '3' and predict._group = 'none'")
                    student_QA_s_a = cursor.fetchall()

                    result5_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '4' and predict._group = 'none'")
                    student_BA_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups and result4_a >= no_of_groups and result5_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()

                            result4 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA = cursor.fetchone()

                            result5 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.MAIN_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA:
                                student_QA_id = student_QA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA:
                                student_BA_id = student_BA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #additional
                            if student_gen:
                                student_gen_id = student_gen['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_gen_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'


                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups and result4_s_a >= no_of_groups and result5_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()

                            result4_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA_s = cursor.fetchone()

                            result5_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict.SECOND_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA_s:
                                student_QA_id_s = student_QA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA_s:
                                student_BA_id_s = student_BA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #additional
                            if student_gen:
                                student_gen_id = student_gen['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_gen_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSCS3A) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                #additional
                                result5_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student5 = cursor.fetchone()

                                if student5:
                                    student5_id = student5['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student5_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'


                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                #additional
                                result5_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student5 = cursor.fetchone()

                                if student5:
                                    student5_id = student5['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student5_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    
                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                remain_students = remain_students - 1
                                                
                                no_of_groups = no_of_groups - 1

                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1


                    mes_s = "Students were successfully formed with 6 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_CS.html', result1_wo=result1_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSCS3A = len(students_BSCS3A), students_BSCS3B = len(students_BSCS3B), students_BSCS3C = len(students_BSCS3C), students_BSCS3D = len(students_BSCS3D), sections_CS=sections_CS)
        #BSCS 3B
        elif program == 'BSCS' and section == '3B':
            if result2 == 0:
                mes_no_studs = "There are no students in this program and section (BSCS-3B) or they might not have predicted their main and secondary roles yet!"
                return render_template('groupings_CS.html', result2_wo=result2_wo, students_wo_group=students_wo_group, mes_no_studs=mes_no_studs, students_all = students_all, students_BSCS3A = len(students_BSCS3A), students_BSCS3B = len(students_BSCS3B), students_BSCS3C = len(students_BSCS3C), students_BSCS3D = len(students_BSCS3D), sections_CS=sections_CS)

            result_check = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.id DESC")
            students_BSCS3B_check = cursor.fetchall()

            if result_check == 0:
                mes_no_studs = "Students in this program and section have already been grouped."
                return render_template('groupings_CS.html', result2_wo=result2_wo, students_wo_group=students_wo_group, mes_no_studs=mes_no_studs, students_all = students_all, students_BSCS3A = len(students_BSCS3A), students_BSCS3B = len(students_BSCS3B), students_BSCS3C = len(students_BSCS3C), students_BSCS3D = len(students_BSCS3D), sections_CS=sections_CS)
            else:
                if group_size == 3:
                    no_of_groups = round(int(len(students_BSCS3B)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()
                            

                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSCS3A) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result3_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student3_remain = cursor.fetchone()

                                    if student3_remain:
                                        student3_remain_id = student3_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_remain_id)))        
                                        mysql.connection.commit()

                                    remain_students = remain_students - 1

                                                
                                no_of_groups = no_of_groups - 1

                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1

                    mes_s = "Students were successfully formed with 3 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_CS.html', result2_wo=result2_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSCS3A = len(students_BSCS3A), students_BSCS3B = len(students_BSCS3B), students_BSCS3C = len(students_BSCS3C), students_BSCS3D = len(students_BSCS3D), sections_CS=sections_CS)
                #When the selected group size is 4
                elif group_size == 4:
                    no_of_groups = round(int(len(students_BSCS3B)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result4_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '3' and predict._group = 'none'")
                    student_QA_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    result4_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '3' and predict._group = 'none'")
                    student_QA_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups and result4_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()

                            result4 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA = cursor.fetchone()
                            

                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA:
                                student_QA_id = student_QA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups and result4_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()

                            result4_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA_s:
                                student_QA_id_s = student_QA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSCS3B) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result4_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student4_remain = cursor.fetchone()

                                    if student4_remain:
                                        student4_remain_id = student4_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_remain_id)))        
                                        mysql.connection.commit()

                                    remain_students = remain_students - 1

                                                
                                no_of_groups = no_of_groups - 1

                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1
                    mes_s = "Students were successfully formed with 4 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_CS.html', result2_wo=result2_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSCS3A = len(students_BSCS3A), students_BSCS3B = len(students_BSCS3B), students_BSCS3C = len(students_BSCS3C), students_BSCS3D = len(students_BSCS3D), sections_CS=sections_CS)

                #When the selected group size is 5
                elif group_size == 5:
                    no_of_groups = round(int(len(students_BSCS3B)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result4_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '3' and predict._group = 'none'")
                    student_QA_a = cursor.fetchall()

                    result5_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '4' and predict._group = 'none'")
                    student_BA_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    result4_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '3' and predict._group = 'none'")
                    student_QA_s_a = cursor.fetchall()

                    result5_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '4' and predict._group = 'none'")
                    student_BA_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups and result4_a >= no_of_groups and result5_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()

                            result4 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA = cursor.fetchone()

                            result5 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA:
                                student_QA_id = student_QA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA:
                                student_BA_id = student_BA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups and result4_s_a >= no_of_groups and result5_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()

                            result4_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA_s = cursor.fetchone()

                            result5_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA_s:
                                student_QA_id_s = student_QA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA_s:
                                student_BA_id_s = student_BA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSCS3B) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result5_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student5_remain = cursor.fetchone()

                                    if student5_remain:
                                        student5_remain_id = student5_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student5_remain_id)))        
                                        mysql.connection.commit()

                                    remain_students = remain_students - 1
                                                
                                no_of_groups = no_of_groups - 1
                            
                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1
                    mes_s = "Students were successfully formed with 5 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_CS.html', result2_wo=result2_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSCS3A = len(students_BSCS3A), students_BSCS3B = len(students_BSCS3B), students_BSCS3C = len(students_BSCS3C), students_BSCS3D = len(students_BSCS3D), sections_CS=sections_CS)
                
                #When the selected group size is 6
                elif group_size == 6:
                    no_of_groups = round(int(len(students_BSCS3B)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result4_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '3' and predict._group = 'none'")
                    student_QA_a = cursor.fetchall()

                    result5_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '4' and predict._group = 'none'")
                    student_BA_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    result4_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '3' and predict._group = 'none'")
                    student_QA_s_a = cursor.fetchall()

                    result5_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '4' and predict._group = 'none'")
                    student_BA_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups and result4_a >= no_of_groups and result5_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()

                            result4 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA = cursor.fetchone()

                            result5 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.MAIN_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA:
                                student_QA_id = student_QA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA:
                                student_BA_id = student_BA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #additional
                            if student_gen:
                                student_gen_id = student_gen['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_gen_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups and result4_s_a >= no_of_groups and result5_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()

                            result4_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA_s = cursor.fetchone()

                            result5_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict.SECOND_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA_s:
                                student_QA_id_s = student_QA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA_s:
                                student_BA_id_s = student_BA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #additional
                            if student_gen:
                                student_gen_id = student_gen['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_gen_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSCS3B) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                #additional
                                result5_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student5 = cursor.fetchone()

                                if student5:
                                    student5_id = student5['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student5_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                #additional
                                result5_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student5 = cursor.fetchone()

                                if student5:
                                    student5_id = student5['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student5_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                remain_students = remain_students - 1
                                                
                                no_of_groups = no_of_groups - 1
                        
                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1
                    mes_s = "Students were successfully formed with 6 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_CS.html', result2_wo=result2_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSCS3A = len(students_BSCS3A), students_BSCS3B = len(students_BSCS3B), students_BSCS3C = len(students_BSCS3C), students_BSCS3D = len(students_BSCS3D), sections_CS=sections_CS)
        #BSCS 3C
        elif program == 'BSCS' and section == '3C':
            if result3 == 0:
                mes_no_studs = "There are no students in this program and section (BSCS-3C) or they might not have predicted their main and secondary roles yet!"
                return render_template('groupings_CS.html', result3_wo=result3_wo, students_wo_group=students_wo_group, mes_no_studs=mes_no_studs, students_all = students_all, students_BSCS3A = len(students_BSCS3A), students_BSCS3B = len(students_BSCS3B), students_BSCS3C = len(students_BSCS3C), students_BSCS3D = len(students_BSCS3D), sections_CS=sections_CS)

            result_check = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.id DESC")
            students_BSCS3C_check = cursor.fetchall()

            if result_check == 0:
                mes_no_studs = "Students in this program and section have already been grouped."
                return render_template('groupings_CS.html', result3_wo=result3_wo, students_wo_group=students_wo_group, mes_no_studs=mes_no_studs, students_all = students_all, students_BSCS3A = len(students_BSCS3A), students_BSCS3B = len(students_BSCS3B), students_BSCS3C = len(students_BSCS3C), students_BSCS3D = len(students_BSCS3D), sections_CS=sections_CS)
            else:
                if group_size == 3:
                    no_of_groups = round(int(len(students_BSCS3C)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()
                            

                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSCS3C) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result3_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student3_remain = cursor.fetchone()

                                    if student3_remain:
                                        student3_remain_id = student3_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_remain_id)))        
                                        mysql.connection.commit()

                                    remain_students = remain_students - 1

                                                
                                no_of_groups = no_of_groups - 1
                            
                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1

                    mes_s = "Students were successfully formed with 3 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_CS.html', result3_wo=result3_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSCS3A = len(students_BSCS3A), students_BSCS3B = len(students_BSCS3B), students_BSCS3C = len(students_BSCS3C), students_BSCS3D = len(students_BSCS3D), sections_CS=sections_CS)
                #When the selected group size is 4
                elif group_size == 4:
                    no_of_groups = round(int(len(students_BSCS3C)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result4_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '3' and predict._group = 'none'")
                    student_QA_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    result4_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '3' and predict._group = 'none'")
                    student_QA_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups and result4_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()

                            result4 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA = cursor.fetchone()
                            

                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA:
                                student_QA_id = student_QA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups and result4_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()

                            result4_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA_s:
                                student_QA_id_s = student_QA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSCS3C) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result4_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student4_remain = cursor.fetchone()

                                    if student4_remain:
                                        student4_remain_id = student4_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_remain_id)))        
                                        mysql.connection.commit()

                                    remain_students = remain_students - 1

                                                
                                no_of_groups = no_of_groups - 1
                            
                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1

                    mes_s = "Students were successfully formed with 4 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_CS.html', result3_wo=result3_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSCS3A = len(students_BSCS3A), students_BSCS3B = len(students_BSCS3B), students_BSCS3C = len(students_BSCS3C), students_BSCS3D = len(students_BSCS3D), sections_CS=sections_CS)

                #When the selected group size is 5
                elif group_size == 5:
                    no_of_groups = round(int(len(students_BSCS3C)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result4_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '3' and predict._group = 'none'")
                    student_QA_a = cursor.fetchall()

                    result5_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '4' and predict._group = 'none'")
                    student_BA_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    result4_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '3' and predict._group = 'none'")
                    student_QA_s_a = cursor.fetchall()

                    result5_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '4' and predict._group = 'none'")
                    student_BA_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups and result4_a >= no_of_groups and result5_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()

                            result4 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA = cursor.fetchone()

                            result5 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA:
                                student_QA_id = student_QA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA:
                                student_BA_id = student_BA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups and result4_s_a >= no_of_groups and result5_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()

                            result4_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA_s = cursor.fetchone()

                            result5_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA_s:
                                student_QA_id_s = student_QA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA_s:
                                student_BA_id_s = student_BA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSCS3C) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result5_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student5_remain = cursor.fetchone()

                                    if student5_remain:
                                        student5_remain_id = student5_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student5_remain_id)))        
                                        mysql.connection.commit()

                                    remain_students = remain_students - 1
                                                
                                no_of_groups = no_of_groups - 1
                            
                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1

                    mes_s = "Students were successfully formed with 5 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_CS.html', result3_wo=result3_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSCS3A = len(students_BSCS3A), students_BSCS3B = len(students_BSCS3B), students_BSCS3C = len(students_BSCS3C), students_BSCS3D = len(students_BSCS3D), sections_CS=sections_CS)
                #When the selected group size is 6
                elif group_size == 6:
                    no_of_groups = round(int(len(students_BSCS3C)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result4_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '3' and predict._group = 'none'")
                    student_QA_a = cursor.fetchall()

                    result5_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '4' and predict._group = 'none'")
                    student_BA_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    result4_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '3' and predict._group = 'none'")
                    student_QA_s_a = cursor.fetchall()

                    result5_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '4' and predict._group = 'none'")
                    student_BA_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups and result4_a >= no_of_groups and result5_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()

                            result4 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA = cursor.fetchone()

                            result5 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.MAIN_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA:
                                student_QA_id = student_QA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA:
                                student_BA_id = student_BA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #additional
                            if student_gen:
                                student_gen_id = student_gen['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_gen_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups and result4_s_a >= no_of_groups and result5_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()

                            result4_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA_s = cursor.fetchone()

                            result5_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict.SECOND_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA_s:
                                student_QA_id_s = student_QA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA_s:
                                student_BA_id_s = student_BA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #additional
                            if student_gen:
                                student_gen_id = student_gen['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_gen_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSCS3C) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                #additional
                                result5_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student5 = cursor.fetchone()

                                if student5:
                                    student5_id = student5['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student5_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                #additional
                                result5_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student5 = cursor.fetchone()

                                if student5:
                                    student5_id = student5['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student5_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                remain_students = remain_students - 1
                                                
                                no_of_groups = no_of_groups - 1
                            
                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '1' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1

                    mes_s = "Students were successfully formed with 6 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_CS.html', result3_wo=result3_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSCS3A = len(students_BSCS3A), students_BSCS3B = len(students_BSCS3B), students_BSCS3C = len(students_BSCS3C), students_BSCS3D = len(students_BSCS3D), sections_CS=sections_CS)

    return render_template('groupings_CS.html', result1_wo=result1_wo, result2_wo=result2_wo, result3_wo=result3_wo,students_all = students_all, students_BSCS3A = len(students_BSCS3A), students_BSCS3B = len(students_BSCS3B), students_BSCS3C = len(students_BSCS3C), students_BSCS3D = len(students_BSCS3D), sections_CS=sections_CS)

#groupings module BSIT
@app.route('/groupings_IT', methods =['GET', 'POST'])
def groupings_IT():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    sections_IT = cursor.execute("SELECT DISTINCT users.section, predict.program FROM users INNER JOIN predict ON users.id = predict.userID WHERE users.program = 'BSIT';")
    sections_IT = cursor.fetchall()

    result5 = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' ORDER BY predict.id DESC")
    students_BSIT3A = cursor.fetchall()

    result6 = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' ORDER BY predict.id DESC")
    students_BSIT3B = cursor.fetchall()

    result7 = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' ORDER BY predict.id DESC")
    students_BSIT3C = cursor.fetchall()

    result8 = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '0' and users.section = '3D' ORDER BY predict.id DESC")
    students_BSIT3D = cursor.fetchall()

    result9 = cursor.execute("SELECT users.id, users.AY, users.firstName, users.lastName, users.section, users.program, predict._group, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '0' ORDER BY predict.id DESC")
    students_all = cursor.fetchall()

    result1_wo = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.id DESC")
    students_BSIT3A_wo = cursor.fetchall()

    result2_wo = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.id DESC")
    students_BSIT3B_wo = cursor.fetchall()

    result3_wo = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.id DESC")
    students_BSIT3C_wo = cursor.fetchall()

    result4_wo = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '0' and users.section = '3D' and predict._group = 'none' ORDER BY predict.id DESC")
    students_BSIT3D_wo = cursor.fetchall()

    result10 = cursor.execute("SELECT users.AY, users.firstName, users.lastName, users.section, users.program, predict._group, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '0' and predict._group = 'none' ORDER BY predict.id DESC")
    students_wo_group = cursor.fetchall()

    if request.method == 'POST' and 'program' in request.form and 'section' in request.form:
        group_size = int(request.form['s_groupSize'])
        program = request.form['program']
        section = request.form['section']

        if program == 'BSIT' and section == '3A':

            if result5 == 0:
                mes_no_studs = "There are no students in this program and section (BSIT-3A) or they might not have predicted their main and secondary roles yet!"
                return render_template('groupings_IT.html', result1_wo=result1_wo,students_wo_group=students_wo_group, mes_no_studs=mes_no_studs, students_all = students_all, students_BSIT3A = len(students_BSIT3A), students_BSIT3B = len(students_BSIT3B), students_BSIT3C = len(students_BSIT3C), students_BSIT3D = len(students_BSIT3D), sections_IT=sections_IT)

            result_check = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.id DESC")
            students_BSIT3A_check = cursor.fetchall()

            if result_check == 0:
                mes_no_studs = "Students in this program and section have already been grouped."
                return render_template('groupings_IT.html', result1_wo=result1_wo, students_wo_group=students_wo_group, mes_no_studs=mes_no_studs, students_all = students_all, students_BSIT3A = len(students_BSIT3A), students_BSIT3B = len(students_BSIT3B), students_BSIT3C = len(students_BSIT3C), students_BSIT3D = len(students_BSIT3D), sections_IT=sections_IT)
            else:
                if group_size == 3:
                    no_of_groups = round(int(len(students_BSIT3A)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()
                            

                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSIT3A) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result3_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student3_remain = cursor.fetchone()

                                    if student3_remain:
                                        student3_remain_id = student3_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_remain_id)))        
                                        mysql.connection.commit()

                                    remain_students = remain_students - 1

                                                
                                no_of_groups = no_of_groups - 1
                            
                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1
    
                    mes_s = "Students were successfully formed with 3 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_IT.html', result1_wo=result1_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSIT3A = len(students_BSIT3A), students_BSIT3B = len(students_BSIT3B), students_BSIT3C = len(students_BSIT3C), students_BSIT3D = len(students_BSIT3D), sections_IT=sections_IT)
                #When the selected group size is 4
                elif group_size == 4:
                    no_of_groups = round(int(len(students_BSIT3A)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result4_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '3' and predict._group = 'none'")
                    student_QA_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    result4_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '3' and predict._group = 'none'")
                    student_QA_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups and result4_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()

                            result4 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA = cursor.fetchone()
                            

                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA:
                                student_QA_id = student_QA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups and result4_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()

                            result4_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA_s:
                                student_QA_id_s = student_QA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSIT3A) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result4_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student4_remain = cursor.fetchone()

                                    if student4_remain:
                                        student4_remain_id = student4_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_remain_id)))        
                                        mysql.connection.commit()

                                    remain_students = remain_students - 1

                                                
                                no_of_groups = no_of_groups - 1
                            
                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1

                    mes_s = "Students were successfully formed with 4 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_IT.html', result1_wo=result1_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSIT3A = len(students_BSIT3A), students_BSIT3B = len(students_BSIT3B), students_BSIT3C = len(students_BSIT3C), students_BSIT3D = len(students_BSIT3D), sections_IT=sections_IT)

                #When the selected group size is 5
                elif group_size == 5:
                    no_of_groups = round(int(len(students_BSIT3A)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result4_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '3' and predict._group = 'none'")
                    student_QA_a = cursor.fetchall()

                    result5_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '4' and predict._group = 'none'")
                    student_BA_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    result4_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '3' and predict._group = 'none'")
                    student_QA_s_a = cursor.fetchall()

                    result5_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '4' and predict._group = 'none'")
                    student_BA_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups and result4_a >= no_of_groups and result5_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()

                            result4 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA = cursor.fetchone()

                            result5 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA:
                                student_QA_id = student_QA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA:
                                student_BA_id = student_BA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups and result4_s_a >= no_of_groups and result5_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()

                            result4_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA_s = cursor.fetchone()

                            result5_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA_s:
                                student_QA_id_s = student_QA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA_s:
                                student_BA_id_s = student_BA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSIT3A) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result5_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student5_remain = cursor.fetchone()

                                    if student5_remain:
                                        student5_remain_id = student5_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student5_remain_id)))        
                                        mysql.connection.commit()

                                    remain_students = remain_students - 1
                                                
                                no_of_groups = no_of_groups - 1
                            
                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1
                    
                    mes_s = "Students were successfully formed with 5 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_IT.html', result1_wo=result1_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSIT3A = len(students_BSIT3A), students_BSIT3B = len(students_BSIT3B), students_BSIT3C = len(students_BSIT3C), students_BSIT3D = len(students_BSIT3D), sections_IT=sections_IT)
                
                #When the selected group size is 6
                elif group_size == 6:
                    no_of_groups = round(int(len(students_BSIT3A)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result4_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '3' and predict._group = 'none'")
                    student_QA_a = cursor.fetchall()

                    result5_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '4' and predict._group = 'none'")
                    student_BA_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    result4_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '3' and predict._group = 'none'")
                    student_QA_s_a = cursor.fetchall()

                    result5_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '4' and predict._group = 'none'")
                    student_BA_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups and result4_a >= no_of_groups and result5_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()

                            result4 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA = cursor.fetchone()

                            result5 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.MAIN_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA:
                                student_QA_id = student_QA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA:
                                student_BA_id = student_BA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #additional
                            if student_gen:
                                student_gen_id = student_gen['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_gen_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups and result4_s_a >= no_of_groups and result5_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()

                            result4_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA_s = cursor.fetchone()

                            result5_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict.SECOND_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA_s:
                                student_QA_id_s = student_QA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA_s:
                                student_BA_id_s = student_BA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #additional
                            if student_gen:
                                student_gen_id = student_gen['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_gen_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSIT3A) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                #additional
                                result5_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student5 = cursor.fetchone()

                                if student5:
                                    student5_id = student5['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student5_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                #additional
                                result5_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student5 = cursor.fetchone()

                                if student5:
                                    student5_id = student5['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student5_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                remain_students = remain_students - 1
                                                
                                no_of_groups = no_of_groups - 1
                            
                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1

                    
                    mes_s = "Students were successfully formed with 6 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_IT.html', result1_wo=result1_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSIT3A = len(students_BSIT3A), students_BSIT3B = len(students_BSIT3B), students_BSIT3C = len(students_BSIT3C), students_BSIT3D = len(students_BSIT3D), sections_IT=sections_IT)
        #BSIT 3B
        elif program == 'BSIT' and section == '3B':
            if result6 == 0:
                mes_no_studs = "There are no students in this program and section (BSIT-3B) or they might not have predicted their main and secondary roles yet!"
                return render_template('groupings_IT.html', result2_wo=result2_wo, students_wo_group=students_wo_group, mes_no_studs=mes_no_studs, students_all = students_all, students_BSIT3A = len(students_BSIT3A), students_BSIT3B = len(students_BSIT3B), students_BSIT3C = len(students_BSIT3C), students_BSIT3D = len(students_BSIT3D), sections_IT=sections_IT)

            result_check = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.id DESC")
            students_BSIT3B_check = cursor.fetchall()

            if result_check == 0:
                mes_no_studs = "Students in this program and section have already been grouped."
                return render_template('groupings_IT.html', result2_wo=result2_wo, students_wo_group=students_wo_group, mes_no_studs=mes_no_studs, students_all = students_all, students_BSIT3A = len(students_BSIT3A), students_BSIT3B = len(students_BSIT3B), students_BSIT3C = len(students_BSIT3C), students_BSIT3D = len(students_BSIT3D), sections_IT=sections_IT)
            else:
                if group_size == 3:
                    no_of_groups = round(int(len(students_BSIT3B)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()
                            

                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSIT3B) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result3_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student3_remain = cursor.fetchone()

                                    if student3_remain:
                                        student3_remain_id = student3_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_remain_id)))        
                                        mysql.connection.commit()

                                    remain_students = remain_students - 1

                                                
                                no_of_groups = no_of_groups - 1
                            
                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1

                    mes_s = "Students were successfully formed with 3 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_IT.html', result2_wo=result2_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSIT3A = len(students_BSIT3A), students_BSIT3B = len(students_BSIT3B), students_BSIT3C = len(students_BSIT3C), students_BSIT3D = len(students_BSIT3D), sections_IT=sections_IT)
                #When the selected group size is 4
                elif group_size == 4:
                    no_of_groups = round(int(len(students_BSIT3B)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result4_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '3' and predict._group = 'none'")
                    student_QA_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    result4_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '3' and predict._group = 'none'")
                    student_QA_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups and result4_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()

                            result4 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA = cursor.fetchone()
                            

                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA:
                                student_QA_id = student_QA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups and result4_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()

                            result4_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA_s:
                                student_QA_id_s = student_QA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSIT3B) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result4_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student4_remain = cursor.fetchone()

                                    if student4_remain:
                                        student4_remain_id = student4_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_remain_id)))        
                                        mysql.connection.commit()

                                    remain_students = remain_students - 1

                                                
                                no_of_groups = no_of_groups - 1
                            
                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1
                    
                    mes_s = "Students were successfully formed with 4 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_IT.html', result2_wo=result2_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSIT3A = len(students_BSIT3A), students_BSIT3B = len(students_BSIT3B), students_BSIT3C = len(students_BSIT3C), students_BSIT3D = len(students_BSIT3D), sections_IT=sections_IT)

                #When the selected group size is 5
                elif group_size == 5:
                    no_of_groups = round(int(len(students_BSIT3B)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result4_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '3' and predict._group = 'none'")
                    student_QA_a = cursor.fetchall()

                    result5_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '4' and predict._group = 'none'")
                    student_BA_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    result4_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '3' and predict._group = 'none'")
                    student_QA_s_a = cursor.fetchall()

                    result5_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '4' and predict._group = 'none'")
                    student_BA_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups and result4_a >= no_of_groups and result5_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()

                            result4 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA = cursor.fetchone()

                            result5 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA:
                                student_QA_id = student_QA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA:
                                student_BA_id = student_BA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups and result4_s_a >= no_of_groups and result5_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()

                            result4_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA_s = cursor.fetchone()

                            result5_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA_s:
                                student_QA_id_s = student_QA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA_s:
                                student_BA_id_s = student_BA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSIT3B) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result5_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student5_remain = cursor.fetchone()

                                    if student5_remain:
                                        student5_remain_id = student5_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student5_remain_id)))        
                                        mysql.connection.commit()

                                    remain_students = remain_students - 1
                                                
                                no_of_groups = no_of_groups - 1
                            
                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1

                    mes_s = "Students were successfully formed with 5 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_IT.html', result2_wo=result2_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSIT3A = len(students_BSIT3A), students_BSIT3B = len(students_BSIT3B), students_BSIT3C = len(students_BSIT3C), students_BSIT3D = len(students_BSIT3D), sections_IT=sections_IT)
                
                #When the selected group size is 6
                elif group_size == 6:
                    no_of_groups = round(int(len(students_BSIT3B)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result4_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '3' and predict._group = 'none'")
                    student_QA_a = cursor.fetchall()

                    result5_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '4' and predict._group = 'none'")
                    student_BA_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    result4_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '3' and predict._group = 'none'")
                    student_QA_s_a = cursor.fetchall()

                    result5_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '4' and predict._group = 'none'")
                    student_BA_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups and result4_a >= no_of_groups and result5_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()

                            result4 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA = cursor.fetchone()

                            result5 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.MAIN_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA:
                                student_QA_id = student_QA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA:
                                student_BA_id = student_BA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #additional
                            if student_gen:
                                student_gen_id = student_gen['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_gen_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups and result4_s_a >= no_of_groups and result5_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()

                            result4_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA_s = cursor.fetchone()

                            result5_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict.SECOND_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA_s:
                                student_QA_id_s = student_QA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA_s:
                                student_BA_id_s = student_BA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #additional
                            if student_gen:
                                student_gen_id = student_gen['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_gen_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSIT3B) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                #additional
                                result5_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student5 = cursor.fetchone()

                                if student5:
                                    student5_id = student5['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student5_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                #additional
                                result5_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student5 = cursor.fetchone()

                                if student5:
                                    student5_id = student5['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student5_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                remain_students = remain_students - 1
                                                
                                no_of_groups = no_of_groups - 1

                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3B' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1
                    mes_s = "Students were successfully formed with 6 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_IT.html', result2_wo=result2_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSIT3A = len(students_BSIT3A), students_BSIT3B = len(students_BSIT3B), students_BSIT3C = len(students_BSIT3C), students_BSIT3D = len(students_BSIT3D), sections_IT=sections_IT)
        #BSIT 3C
        elif program == 'BSIT' and section == '3C':
            if result7 == 0:
                mes_no_studs = "There are no students in this program and section (BSIT-3C) or they might not have predicted their main and secondary roles yet!"
                return render_template('groupings_IT.html', result3_wo=result3_wo, students_wo_group=students_wo_group, mes_no_studs=mes_no_studs, students_all = students_all, students_BSIT3A = len(students_BSIT3A), students_BSIT3B = len(students_BSIT3B), students_BSIT3C = len(students_BSIT3C), students_BSIT3D = len(students_BSIT3D), sections_IT=sections_IT)

            result_check = cursor.execute("SELECT predict.id, users.firstName, users.lastName, users.section, predict.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.id DESC")
            students_BSIT3C_check = cursor.fetchall()

            if result_check == 0:
                mes_no_studs = "Students in this program and section have already been grouped."
                return render_template('groupings_IT.html', result3_wo=result3_wo, students_wo_group=students_wo_group, mes_no_studs=mes_no_studs, students_all = students_all, students_BSIT3A = len(students_BSIT3A), students_BSIT3B = len(students_BSIT3B), students_BSIT3C = len(students_BSIT3C), students_BSIT3D = len(students_BSIT3D), sections_IT=sections_IT)
            else:
                if group_size == 3:
                    no_of_groups = round(int(len(students_BSIT3C)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()
                            

                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSIT3C) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result3_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student3_remain = cursor.fetchone()

                                    if student3_remain:
                                        student3_remain_id = student3_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_remain_id)))        
                                        mysql.connection.commit()

                                    remain_students = remain_students - 1

                                                
                                no_of_groups = no_of_groups - 1
                            
                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1

                    mes_s = "Students were successfully formed with 3 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_IT.html', result3_wo=result3_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSIT3A = len(students_BSIT3A), students_BSIT3B = len(students_BSIT3B), students_BSIT3C = len(students_BSIT3C), students_BSIT3D = len(students_BSIT3D), sections_IT=sections_IT)
                #When the selected group size is 4
                elif group_size == 4:
                    no_of_groups = round(int(len(students_BSIT3C)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result4_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '3' and predict._group = 'none'")
                    student_QA_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    result4_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '3' and predict._group = 'none'")
                    student_QA_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups and result4_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()

                            result4 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA = cursor.fetchone()
                            

                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA:
                                student_QA_id = student_QA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups and result4_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()

                            result4_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA_s:
                                student_QA_id_s = student_QA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSIT3C) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result4_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student4_remain = cursor.fetchone()

                                    if student4_remain:
                                        student4_remain_id = student4_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_remain_id)))        
                                        mysql.connection.commit()

                                    remain_students = remain_students - 1

                                                
                                no_of_groups = no_of_groups - 1
                            
                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1
                    
                    mes_s = "Students were successfully formed with 4 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_IT.html', result3_wo=result3_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSIT3A = len(students_BSIT3A), students_BSIT3B = len(students_BSIT3B), students_BSIT3C = len(students_BSIT3C), students_BSIT3D = len(students_BSIT3D), sections_IT=sections_IT)

                #When the selected group size is 5
                elif group_size == 5:
                    no_of_groups = round(int(len(students_BSIT3C)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result4_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '3' and predict._group = 'none'")
                    student_QA_a = cursor.fetchall()

                    result5_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '4' and predict._group = 'none'")
                    student_BA_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    result4_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '3' and predict._group = 'none'")
                    student_QA_s_a = cursor.fetchall()

                    result5_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '4' and predict._group = 'none'")
                    student_BA_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups and result4_a >= no_of_groups and result5_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()

                            result4 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA = cursor.fetchone()

                            result5 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA:
                                student_QA_id = student_QA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA:
                                student_BA_id = student_BA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups and result4_s_a >= no_of_groups and result5_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()

                            result4_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA_s = cursor.fetchone()

                            result5_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA_s:
                                student_QA_id_s = student_QA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA_s:
                                student_BA_id_s = student_BA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSIT3C) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result5_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student5_remain = cursor.fetchone()

                                    if student5_remain:
                                        student5_remain_id = student5_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student5_remain_id)))        
                                        mysql.connection.commit()

                                    remain_students = remain_students - 1
                                                
                                no_of_groups = no_of_groups - 1
                            
                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1
                    
                    mes_s = "Students were successfully formed with 5 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_IT.html', result3_wo=result3_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSIT3A = len(students_BSIT3A), students_BSIT3B = len(students_BSIT3B), students_BSIT3C = len(students_BSIT3C), students_BSIT3D = len(students_BSIT3D), sections_IT=sections_IT)
                
                #When the selected group size is 6
                elif group_size == 6:
                    no_of_groups = round(int(len(students_BSIT3C)/group_size))
                    group_iterator = 0
                    group_iterator_inner = 0
                    result1_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '0' and predict._group = 'none'")
                    student_LP_a = cursor.fetchall()
                    
                    result2_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '1' and predict._group = 'none'")
                    student_PM_a = cursor.fetchall() 

                    result3_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_a = cursor.fetchall()

                    result4_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '3' and predict._group = 'none'")
                    student_QA_a = cursor.fetchall()

                    result5_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '4' and predict._group = 'none'")
                    student_BA_a = cursor.fetchall()

                    result1_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '0' and predict._group = 'none'")
                    student_LP_s_a = cursor.fetchall()
                    
                    result2_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '1' and predict._group = 'none'")
                    student_PM_s_a = cursor.fetchall()
                    
                    result3_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '2' and predict._group = 'none'")
                    student_UI_UX_s_a = cursor.fetchall()

                    result4_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '3' and predict._group = 'none'")
                    student_QA_s_a = cursor.fetchall()

                    result5_s_a = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '4' and predict._group = 'none'")
                    student_BA_s_a = cursor.fetchall()

                    if result1_a >= no_of_groups and result2_a >= no_of_groups and result3_a >= no_of_groups and result4_a >= no_of_groups and result5_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                            
                            result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP = cursor.fetchone()
                            
                            result2 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM = cursor.fetchone() 

                            result3 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX = cursor.fetchone()

                            result4 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA = cursor.fetchone()

                            result5 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.MAIN_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP:
                                student_LP_id = student_LP['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM:
                                student_PM_id = student_PM['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id)))        
                                mysql.connection.commit()
            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX:
                                student_UI_UX_id = student_UI_UX['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA:
                                student_QA_id = student_QA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA:
                                student_BA_id = student_BA['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #additional
                            if student_gen:
                                student_gen_id = student_gen['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_gen_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1
                    elif result1_s_a >= no_of_groups and result2_s_a >= no_of_groups and result3_s_a >= no_of_groups and result4_s_a >= no_of_groups and result5_s_a >= no_of_groups:
                        while no_of_groups > 0:
                            group_iterator = group_iterator + 1
                            result0 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' LIMIT 1")
                            student_gen = cursor.fetchone()
                    
                            result1_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '0' and predict._group = 'none' LIMIT 1")
                            student_LP_s = cursor.fetchone()
                            
                            result2_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '1' and predict._group = 'none' LIMIT 1")
                            student_PM_s = cursor.fetchone()
                            
                            result3_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '2' and predict._group = 'none' LIMIT 1")
                            student_UI_UX_s = cursor.fetchone()

                            result4_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '3' and predict._group = 'none' LIMIT 1")
                            student_QA_s = cursor.fetchone()

                            result5_s = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict.SECOND_ROLE = '4' and predict._group = 'none' LIMIT 1")
                            student_BA_s = cursor.fetchone()
                            
                            #Lead programmer
                            if student_LP_s:
                                student_LP_id_s = student_LP_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_LP_id_s)))        
                                mysql.connection.commit()
                        
                            else:
                                mes='unexpected error occured!'
                            
                            #Project Manager 
                            if student_PM_s:
                                student_PM_id_s = student_PM_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_PM_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #UI/UX Designer
                            if student_UI_UX_s:
                                student_UI_UX_id_s = student_UI_UX_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_UI_UX_id_s)))        
                                mysql.connection.commit()
                            else:
                                mes='unexpected error occured!'
                            
                            #QA Engineer
                            if student_QA_s:
                                student_QA_id_s = student_QA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_QA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #BA
                            if student_BA_s:
                                student_BA_id_s = student_BA_s['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_BA_id_s)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'
                            
                            #additional
                            if student_gen:
                                student_gen_id = student_gen['id']
                                cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student_gen_id)))        
                                mysql.connection.commit()
                            
                            else:
                                mes='unexpected error occured!'

                            no_of_groups = no_of_groups - 1     
                    else:
                        mes="dasdsadsad"
                        remain_students = int(len(students_BSIT3C) % group_size)
                        if remain_students == 0:
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                #additional
                                result5_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student5 = cursor.fetchone()

                                if student5:
                                    student5_id = student5['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student5_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                                
                                no_of_groups = no_of_groups - 1    
                        else:
                            mes="pass me cok"
                            no_of_groups_inner = no_of_groups
                            while no_of_groups > 0:
                                group_iterator = group_iterator + 1
                                while no_of_groups_inner > 0:
                                    group_iterator_inner = group_iterator_inner + 1
                                    mes = 'pass'
                                    result1 = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student_LP = cursor.fetchone()

                                    #Top students based on their average grade for programming courses
                                    if student_LP:
                                        student_LP_id = student_LP['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator_inner), int(student_LP_id)))        
                                        mysql.connection.commit()
                                
                                    else:
                                        mes='unexpected error occured!'
                                    
                                    no_of_groups_inner = no_of_groups_inner - 1

                                # - outer
                                result1_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student1 = cursor.fetchone()

                                if student1:
                                    student1_id = student1['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student1_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result2_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student2 = cursor.fetchone()

                                if student2:
                                    student2_id = student2['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student2_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result3_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student3 = cursor.fetchone()

                                if student3:
                                    student3_id = student3['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student3_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                result4_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student4 = cursor.fetchone()

                                if student4:
                                    student4_id = student4['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student4_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'
                                
                                #additional
                                result5_out = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3A' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                student5 = cursor.fetchone()

                                if student5:
                                    student5_id = student5['id']
                                    cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student5_id)))        
                                    mysql.connection.commit()
                            
                                else:
                                    mes='unexpected error occured!'

                                if remain_students > 0:
                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                remain_students = remain_students - 1
                                                
                                no_of_groups = no_of_groups - 1

                            if no_of_groups == 0 and remain_students > 0:
                                while remain_students > 0:

                                    if group_iterator == 0 and remain_students > 0:
                                        group_iterator = group_iterator + 1

                                    result6_out_remain = cursor.execute("SELECT users.firstName, users.lastName, users.section, predict.id, predict.programming_avg FROM predict INNER JOIN users on users.id = predict.userID WHERE predict.program = '0' and users.section = '3C' and predict._group = 'none' ORDER BY predict.programming_avg ASC LIMIT 1")
                                    student6_remain = cursor.fetchone()

                                    if student6_remain:
                                        student6_remain_id = student6_remain['id']
                                        cursor.execute('UPDATE predict SET _group = % s WHERE id = % s', (int(group_iterator), int(student6_remain_id)))        
                                        mysql.connection.commit()

                                    group_iterator = group_iterator - 1
                                    remain_students = remain_students - 1
                    mes_s = "Students were successfully formed with 6 members each group. However, some groups will have additional member/s if the class size is not even.!"
                    return render_template('groupings_IT.html', result3_wo=result3_wo, mes=mes, mes_s=mes_s, students_all = students_all, students_BSIT3A = len(students_BSIT3A), students_BSIT3B = len(students_BSIT3B), students_BSIT3C = len(students_BSIT3C), students_BSIT3D = len(students_BSIT3D), sections_IT=sections_IT)
    
    return render_template('groupings_IT.html', result1_wo=result1_wo, result2_wo=result2_wo, result3_wo=result3_wo, students_all = students_all, students_BSIT3A = len(students_BSIT3A), students_BSIT3B = len(students_BSIT3B), students_BSIT3C = len(students_BSIT3C), students_BSIT3D = len(students_BSIT3D), sections_IT= sections_IT)

@app.route('/student_records')
def student_records():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    result = cursor.execute("SELECT users.id, users.AY, users.firstName, users.lastName, users.section, users.program, predict.MAIN_ROLE, predict.SECOND_ROLE FROM users INNER JOIN predict ON users.id = predict.userID ORDER BY predict.id DESC")
    student = cursor.fetchall()
    return render_template('student_records.html', student=student)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('firstName', None)
    session.pop('lastName', None)
    session.pop('email', None)
    session.pop('password', None)
    session.pop('has_record', None)
    session.pop('no_predicted_studs_result_IT', None)
    session.pop('no_predicted_studs_data_IT', None)
    session.pop('no_predicted_studs_result_CS', None)
    session.pop('no_predicted_studs_data_CS', None)
    session.pop('no_registered_studs_result', None)
    session.pop('no_registered_studs_data_10', None)
    session.pop('no_predicted_studs_result_10_IT', None)
    session.pop('no_predicted_studs_data_10_IT', None)
    session.pop('no_predicted_studs_result_10_CS', None)
    session.pop('no_predicted_studs_data_10_CS', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST'  and 'userType' in request.form and 'firstName' in request.form  and 'lastName' in request.form  and 'password' in request.form and 'email' in request.form and 'program' in request.form  and 'section' in request.form :
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        password = request.form['password']
        email = request.form['email']
        section = request.form['section']
        program = request.form['program']
        userType = request.form['userType']
        d1 = datetime.datetime.now()
        AY = ""

        if d1.month >= 7 and d1.month <= 12:
            AY = str(d1.year) + "-" + str(d1.year + 1) 
        elif d1.month >= 1 and d1.month <= 6:
            AY = str(d1.year - 1) + "-" + str(d1.year)

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
            if userType == 'student':
                cursor.execute('INSERT INTO users (AY, userType, firstName, lastName, email, password, section, program) VALUES (% s, % s, % s, % s, % s, % s, % s, % s)', (AY, userType, firstName, lastName, email, password, section, program,))
                mysql.connection.commit()
                mesage = 'You have successfully registered!'
            else:
                cursor.execute('INSERT INTO users (AY, userType, firstName, lastName, email, password) VALUES (% s, % s, % s, % s, % s, % s)', (AY, userType, firstName, lastName, email, password,))
                mysql.connection.commit()
                mesage = 'You have successfully registered!'

    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage = mesage)


if __name__ == "__main__":
    app.run(debug=True)

