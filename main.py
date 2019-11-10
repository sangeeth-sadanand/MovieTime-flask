"""Main file for app."""
from flask import Flask, render_template, session, request, abort, redirect, url_for, flash, get_flashed_messages
from modules.admin import admin
from modules.user import user
from modules.Db_functions import get_user_data, insert_user_data, get_movie_data, connect_db,get_show_data


app = Flask(__name__)
app.secret_key = 'HELLO_FLASK'
app.register_blueprint(admin)
app.register_blueprint(user)


app.config['now_showing'] = get_movie_data(sel = "id,name", where = 'now_showing = 0')
# Error handling.
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_handling/404.html')

@app.errorhandler(500)
def server_error(e):
    return render_template('error_handling/404.html')

########################################## HOME ########################################
@app.route('/home')
@app.route('/')
def home():
    app.config['now_showing'] = get_movie_data(sel = "id,name", where = 'now_showing = 0')
    session['now_showing'] = app.config['now_showing']
    data1 = get_movie_data(sel='name, languages, genes, poster_url', where = 'now_showing = 0')
    if not data1:
        data1= [('','','','')]
    data2 = get_movie_data(sel='name, languages, genes, poster_url', where = 'now_showing = 1')
    if not data2:
        data2= [('','','','')]
    return render_template('home.html',data1=data1, data2=data2)

############################################## NOW SHOWING ###########################################
@app.route("/now_showing")
def now_showing():
    session['now_showing'] = app.config['now_showing']
    data1 = get_movie_data(where = 'now_showing = 0')
    if not data1:
        data1 =[('','','','','','','','','','')]
    return render_template('now_showing.html',data = data1)

############################################## COMING SOON ########################################
@app.route("/coming_soon")
def coming_soon():
    session['now_showing'] = app.config['now_showing']
    data1 = get_movie_data(where = 'now_showing = 1')
    if not data1:
        data1 =[('','','','','','','','','','')]
    return render_template('now_showing.html',data = data1)
################################################ BOOK NOW #########################################

@app.route('/book_now/<id>')
def book_now(id):
    from datetime import datetime, timedelta
    today = datetime.now() 
    data ={}
    today1 = today + timedelta(days=1)
    data1 = get_movie_data(where = f"id = {id}")[0]
    data['today'] = datetime.strftime(today,'%Y-%m-%d')
    data['today1'] = datetime.strftime(today1,'%Y-%m-%d')
    show_data_today = get_show_data(sel = "id,language,from_time", where = f"date = '{data['today']}' AND movie_id = {id} ORDER BY from_time ASC")
    show_data_today1 = get_show_data(sel = "id,language,from_time", where = f"date = '{data['today1']}' AND movie_id = {id} ORDER BY from_time ASC")
    print(show_data_today)
    return render_template("book_now.html", data = data, movie_data = data1, show_today = show_data_today, show_today1 = show_data_today1)

############################################### Booked ticket ###################################

@app.route("/booked_ticket")
def booked_ticket():
    [conn,cur] = connect_db()
    try:
        command = f"SELECT  m.name,s.date, s.from_time, b.grand_total, s.screen,b.seats,b.id \
                    FROM bill b\
                    LEFT JOIN  show_list s ON b.show_id = s.id \
                    LEFT JOIN movie_list m ON s.movie_id = m.id \
                    WHERE b.user_id = {session.get('login_id')} \
                    ORDER BY b.date_time DESC"
        cur.execute(command)
        data = cur.fetchall()
        return render_template("/bookticket/booked_ticket.html", data = data)
    finally:
        conn.close()
############################################### LOGIN ############################################
@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('user/login.html')
    else:
        email = request.form['username']
        password = request.form['passwd']
        data = get_user_data(where  = "email = '"+email+"'" ) 
        if len(data) == 1:
            if data[0][4] == password  :
                session['login_username'] = data[0][1] +' '+ data[0][2]
                flash(f"Welcome {session['login_username']}, login successful ", 'success')
                session['login'] = True
                session['login_type'] = data[0][5]
                session['login_id'] = data[0][0]
                return redirect(url_for('home'))
            else:
                flash('Authentication failed', 'error')
                return redirect(url_for('login'))
        else:
            flash('Authentication failed', 'error')
            return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session['login_username'] = 'Guest'
    session['login_type'] = None
    session['login'] = False
    flash('Logged out successful')
    return redirect(url_for('home'))

########################################## REGISTRATION #########################################
@app.route('/register-user', methods = ['GET','POST'])
def register_user():
    try:
        if request.method == 'GET':
            return render_template('user/register_user.html')
        else:
            data = get_user_data(sel = 'email' )
            data = list(map(lambda x: x[0],data))
            print(data)
            user = {}
            user['firstname'] = request.form['firstname']
            user['lastname'] = request.form['lastname']
            user['email'] = request.form['username']
            user['password'] = request.form['passwd']
            user['type'] = 'user'
            if (user['email'] not in data):
                insert_user_data(user)
                flash(f"User with email {user['email']} added",'success')
            return redirect(url_for('login'))
    except:
        abort(404)

@app.route('/ajax/email')
def ajax_email():
    email = request.args['email']
    email = get_user_data(where = "email = '" + email +"'")
    print(len(email))
    if len(email) == 0:
        return "true"
    else:
        return "false"

################################################# FORGOT PASSWORD #######################################
@app.route('/forgot_password', methods=["POST","GET"])
def forgot_password():
    if request.method=="GET": 
        return render_template('user/forgot_password.html')
    else:
        email = request.form["emailid"]
        data = get_user_data(where = "email = '" + email +"'")
        if data:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            mail_content = f"Your password for the Movie Time account is: {data[0][4]}. Please change the password for security reasons." 
            #The mail addresses and password
            sender_address = 'prognoz.exceptions@gmail.com'
            sender_pass = 'exc654321'
            receiver_address = email
            #Setup the MIME
            message = MIMEMultipart()
            message['From'] = sender_address
            message['To'] = receiver_address
            message['Subject'] = 'MovieTime ticket id {id}.'   #The subject line
            #The body and the attachments for the mail
            message.attach(MIMEText(mail_content, 'plain'))
            #Create SMTP session for sending the mail
            session1 = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
            session1.starttls() #enable security
            session1.login(sender_address, sender_pass) #login with mail_id and password
            text = message.as_string()
            session1.sendmail(sender_address, receiver_address, text)
            session1.quit()
            flash("Password sent to your email id")
            return redirect(url_for('login'))
        else: 
            flash("Please use registered email id and try again OR create new account",'error')
            return redirect(url_for('forgot_password'))

#################################################### VIEW PROFILE #################################################
@app.route("/view_profile", methods = ["GET","POST"])
def view_profile():
    if login:
        if request.method == "GET":
            data = get_user_data(where = "id = " + str(session.get('login_id')) +"")
            print(data)
            return render_template("user/view_profile.html",data=data[0])
        else:
            password = request.form['passwd']
            [conn,cur] = connect_db()
            cur.execute(f"UPDATE `user` SET password = '{password}' WHERE id ={str(session.get('login_id'))}")
            flash('Password Changed', 'Message')
            return redirect('home')

if __name__ == "__main__":
    app.run(debug = True)