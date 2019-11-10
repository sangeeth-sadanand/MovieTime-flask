from flask import Blueprint,Flask, render_template,session,request,abort,redirect,url_for,flash,get_flashed_messages
from werkzeug.utils import secure_filename
from datetime import datetime as dt

from modules.Db_functions import *

admin = Blueprint('admin', __name__)

@admin.route('/admin/home')
def admin_home():
    if session.get('login') and session.get('login_type') == 'admin':
        return render_template('admin/home.html')
    else:
        flash('Invalid  login', 'error')
        return redirect(url_for('login'))


######################################################## Manage Movies ##########################################
@admin.route('/admin/manage_movies/show')
def admin_manage_movie_show():
    if session.get('login') and session.get('login_type') == 'admin':
        data = get_movie_data()
        return render_template('/admin/manage_movies/show.html',data=data)


#################################################################################################################
@admin.route("/admin/manage_movies/add", methods=['GET', 'POST'])
def admin_manage_movie_add():
    if session.get('login') and session.get('login_type') == 'admin': 
        if(request.method == 'GET'):
            return render_template("/admin/manage_movies/add.html")
        else:
            data = {}
            data['name'] = request.form['name'].replace("'",'`')
            data['languages'] = request.form['language'].replace("'",'`')
            data['genes'] = request.form['genes'].replace("'",'`')
            data['runtime'] = request.form['runtime'].replace("'",'`')
            data['rating'] = request.form['rating'].replace("'",'`')
            data['status'] = request.form['status'].replace("'",'`')
            data['release_date'] = request.form['date'].replace("'",'`')
            data['desc'] = request.form['desc'].replace("'",'`')
            file = request.files['file']
            filename = secure_filename(file.filename)
            filename = data['name'] + '_' + filename
            file.save('static/img/Movies/' + filename)
            data['filename'] = filename
            insert_movie_data(data)
            return redirect(url_for("admin.admin_manage_movie_show"))

#################################################################################################################
@admin.route("/admin/manage_movies/edit/<id>",methods = ['GET', 'POST'])
def admin_manage_movie_edit(id):
    if session.get('login') and session.get('login_type') == 'admin':
        if(request.method=='GET'):
            da = get_movie_data(where = 'id = ' + str(id))
            da = da[0]
            data = {}
            data['id'] = da[0]
            data['name'] = da[1]
            data['languages'] = da[2] 
            data['genes'] =  da[3]
            data['runtime'] = "0"+str(da[4])[:-3]
            data['rating'] = da[5]
            data['status'] =  da[6]
            data['release_date'] = str(da[8])
            print('r date #########################',data['release_date'])
            data['desc'] = da[9]
            data['filename'] =  da[7]
            return render_template("/admin/manage_movies/edit.html", data=data)
        else:
            data = {}
            data['id'] = request.form['id']
            data['name'] = request.form['name'].replace("'",'`')
            data['languages'] = request.form['language'].replace("'",'`')
            data['genes'] = request.form['genes'].replace("'",'`')
            data['runtime'] = request.form['runtime'].replace("'",'`')
            data['rating'] = request.form['rating'].replace("'",'`')
            data['status'] = request.form['status'].replace("'",'`')
            data['release_date'] = request.form['date'].replace("'",'`')
            data['desc'] = request.form['desc'].replace("'",'`')
            old_filename = request.form['old_filename']
            if (request.form['image_uploaded']=='True'):
                file = request.files['file']
                filename = secure_filename(file.filename)
                filename = filename
                file.save('static/img/Movies/' + filename)
                import os
                print(old_filename)
                if os.path.exists('static/img/Movies/' + old_filename):
                    os.remove('static/img/Movies/' + old_filename)
                else:
                    print(f"File static/img/Movies/' {old_filename} not found")
                    print('Delete files manually')
                data['filename'] = filename
            else:
                data['filename'] = old_filename
            print(data)
            update_movie_data(data)
            return redirect(url_for("admin.admin_manage_movie_show"))

#################################################################################################################
@admin.route("/admin/manage_movies/delete/<id>",methods = ['GET', 'POST'])
def admin_manage_movie_delete(id):
    if session.get('login') and session.get('login_type') == 'admin':
        if request.method == 'GET' :
            da = get_movie_data(where = 'id = ' + str(id))
            da= da[0]
            data = {}
            data['id'] = da[0]
            data['name'] = da[1]
            return render_template('/admin/manage_movies/delete.html',data = data)
        else:
            if (request.form['action']== 'Yes'):
                id = request.form['id']
                delete_movie_data(id)
                return redirect(url_for("admin.admin_manage_movie_show"))
            else:
                return redirect(url_for("admin.admin_manage_movie_show"))
    else:
        return redirect(url_for('login'))


##################################################### Show time home ############################################
@admin.route("/admin/showtime/show")
def admin_showtime_show():
    if session.get('login') and session.get('login_type') == 'admin' :
        from datetime import datetime, timedelta
        today = datetime.now() 
        today1 = today + timedelta(days=1)
        today2 = today1 + timedelta(days=1)
        data = {}
        data['today'] = datetime.strftime(today,'%Y-%m-%d')
        data['today1'] = datetime.strftime(today1,'%Y-%m-%d')
        data['today2'] = datetime.strftime(today2,'%Y-%m-%d')
        data['screen1_today2'] = get_show_data_join_movie(sel = 's.from_time,s.to_time,s.id,m.name,s.language',
                                                         where = f"date = '{data['today2']}' AND screen = 1")
        data['screen2_today2'] = get_show_data_join_movie(sel = 's.from_time,s.to_time,s.id,m.name,s.language',
                                                         where = f"date = '{data['today2']}' AND screen = 2")
        data['screen3_today2'] = get_show_data_join_movie(sel = 's.from_time,s.to_time,s.id,m.name,s.language',
                                                         where = f"date = '{data['today2']}' AND screen = 3")
        ###################################################################################################################
        data['screen1_today1'] = get_show_data_join_movie(sel = 's.from_time,s.to_time,s.id,m.name,s.language',
                                                         where = f"date = '{data['today1']}' AND screen = 1")
        data['screen2_today1'] = get_show_data_join_movie(sel = 's.from_time,s.to_time,s.id,m.name,s.language',
                                                         where = f"date = '{data['today1']}' AND screen = 2")
        data['screen3_today1'] = get_show_data_join_movie(sel = 's.from_time,s.to_time,s.id,m.name,s.language',
                                                         where = f"date = '{data['today1']}' AND screen = 3")
        ###################################################################################################################
        data['screen1_today'] = get_show_data_join_movie(sel = 's.from_time,s.to_time,s.id,m.name,s.language',
                                                         where = f"date = '{data['today']}' AND screen = 1")
        data['screen2_today'] = get_show_data_join_movie(sel = 's.from_time,s.to_time,s.id,m.name,s.language',
                                                         where = f"date = '{data['today']}' AND screen = 2")
        data['screen3_today'] = get_show_data_join_movie(sel = 's.from_time,s.to_time,s.id,m.name,s.language',
                                                         where = f"date = '{data['today']}' AND screen = 3")
        ###################################################################################################################
        return render_template("/admin/showtime/show.html", data = data)
    else:
        return redirect(url_for('login'))


#################################################################################################################
@admin.route("/admin/showtime/add/<screen>", methods=['POST','GET'])
def admin_showtime_add(screen):
    if session.get('login') and session.get('login_type') == 'admin' :
        if request.method == 'GET' :
            data={}
            data['screen'] = screen
            from datetime import datetime, timedelta
            today2 = datetime.now() + timedelta(days=2)
            data['date'] = datetime.strftime(today2,'%Y-%m-%d')
            dta =get_movie_data(sel = 'id, name, languages, run_time', where = f"release_date <= '{data['date']}'")
            movie_data = {}
            for dat in dta:
                temp =[dat[1],dat[3].seconds//60,list(map(lambda x: x.strip(),list(dat[2].split(','))))]
                movie_data[dat[0]]=temp
            #da = get_movie_data(where = 'id = ' + str(id))
            return render_template("/admin/showtime/add.html", data = data, movie_data = movie_data)
        else:
            data={}
            data['screen'] = request.form['screen']
            data['movie'] = request.form['movie']
            data['date'] = request.form['date']
            data['languages'] = request.form['language']
            data['start_time'] = request.form['start_time']
            data['run_time'] = request.form['run_time']
            data['break_time'] = request.form['break_time']
            data['gap_time'] = request.form['gap_time']
            data['end_time'] = request.form['end_time']
            data['plat'] = request.form['plat']
            data['gold'] = request.form['gold']
            data['silv'] = request.form['silv']
            print('*'*25+'\n'+str(data)+'\n'+'*'*25)
            insert_show_data(data)
            return redirect(url_for('admin.admin_showtime_show'))
    else:
        return redirect(url_for('login'))


@admin.route('/ajax/showtime')
def ajax_checkshowtime():
    screen = request.args['screen']
    start_time = request.args['start_time']
    end_time = request.args['end_time']
    date = request.args['date']
    
    data = get_show_data(sel = 'id', where = f"('{start_time}' between `from_time` and `to_time`\
        OR '{end_time}' between from_time and to_time\
        OR from_time between '{start_time}' and '{end_time}'\
        OR to_time between '{start_time}' and '{end_time}')\
        AND screen = '{screen}' AND date = '{date}'")
    if len(data) == 0 :
        return 'true'
    else:
        return 'false'


@admin.route("/admin/showtime/edit/<id>", methods=['POST','GET'])
def admin_showtime_edit(id):
    if session.get('login') and session.get('login_type') == 'admin' :
        if request.method == 'GET' :
            from datetime import timedelta
            d = get_show_data(where=f"id = {id}")[0]
            data = {}
            data['id'] = d[0]
            data['screen']= d[1]    
            data['movie_id']= d[2]    
            data['date']= d[3]    
            data['language']= d[4]
            if d[5] < timedelta(hours=10):
                data['from_time']= '0' + str(d[5])[:-3]
            else:
                data['from_time']= str(d[5])[:-3]
            data['run_time']= d[6]    
            data['break_time']= d[7]    
            data['gap_time']= d[8]    
            if d[9] < timedelta(hours=10):
                data['to_time']= '0' + str(d[9])[:-3]    
            else:
                data['to_time']= str(d[9])[:-3] 
            data['plat']= d[10]    
            data['gold']= d[11]
            data['silv']= d[12]

            dta =get_movie_data(sel = 'id, name, languages, run_time', where = f"release_date <= '{data['date']}'")
            movie_data = {}
            for dat in dta:
                temp =[dat[1],dat[3].seconds//60,list(map(lambda x: x.strip(),list(dat[2].split(','))))]
                movie_data[dat[0]]=temp
                print(temp)
            return render_template("/admin/showtime/edit.html", data = data, movie_data = movie_data)
        else:
            data={}
            data['id'] = request.form['id']
            data['screen'] = request.form['screen']
            data['movie'] = request.form['movie']
            data['date'] = request.form['date']
            data['languages'] = request.form['language']
            data['start_time'] = request.form['start_time']
            data['run_time'] = request.form['run_time']
            data['break_time'] = request.form['break_time']
            data['gap_time'] = request.form['gap_time']
            data['end_time'] = request.form['end_time']
            data['plat'] = request.form['plat']
            data['gold'] = request.form['gold']
            data['silv'] = request.form['silv']
            print('*'*25+'\n'+str(data)+'\n'+'*'*25)
            update_show_data(data)
            return redirect(url_for('admin.admin_showtime_show'))
    else:
        return redirect(url_for('login'))


@admin.route('/ajax/showtime_id')
def ajax_checkshowtime_id():
    screen = request.args['screen']
    start_time = request.args['start_time']
    end_time = request.args['end_time']
    date = request.args['date']
    cid = request.args['id']
    
    data = get_show_data(sel = 'id', where = f"('{start_time}' between `from_time` and `to_time`\
        OR '{end_time}' between from_time and to_time\
        OR from_time between '{start_time}' and '{end_time}'\
        OR to_time between '{start_time}' and '{end_time}')\
        AND screen = '{screen}' AND date = '{date}' AND id <> {cid}")
    if len(data) == 0 :
        return 'true'
    else:
        return 'false'


@admin.route("/admin/showtime/delete/<id>", methods=['POST','GET'])
def admin_showtime_delete(id):
    if session.get('login') and session.get('login_type') == 'admin':
        if request.method == 'GET' :
            d = get_show_data_join_movie(sel = 's.from_time,s.to_time,s.id,m.name,s.language',
                                                         where = f"s.id = {id}")[0]
            return render_template('/admin/showtime/delete.html',data = d)
        else:
            if (request.form['action']== 'Yes'):
                id = request.form['id']
                delete_movie_data(id)
                flash("Show time deleted")
                return redirect(url_for("admin.admin_showtime_show"))
            else:
                return redirect(url_for("admin.admin_showtime_show"))
    else:
        return redirect(url_for('login'))


@admin.route("/admin/showtime/detail/<id>", methods=['POST','GET'])
def admin_showtime_detail(id):
    pass

@admin.route("/admin/bill", methods = ['GET', 'POST'])
def admin_bill():
    if session.get('login') and session.get('login_type') == 'admin':
        if request.method == "GET" :
            try:
                [conn,cur] = connect_db()
                command = f"SELECT  b.id, m.name, s.language, b.date_time, u.email, b.seats,b.total, b.sgst,b.cgst,b.grand_total \
                            FROM bill b\
                            LEFT JOIN  show_list s ON b.show_id = s.id \
                            LEFT JOIN movie_list m ON s.movie_id = m.id \
                            LEFT JOIN user u ON u.id = b.user_id \
                            ORDER BY b.date_time DESC"
                cur.execute(command)
                data = cur.fetchall()
                cur.execute('SELECT sum(total), sum(sgst),sum(cgst), sum(grand_total) FROM bill')
                ttl = cur.fetchone()
                return render_template("/admin/bill/show.html", data = data, ttl = ttl)
            finally:
                conn.close()
        else:
            date_from = str(request.form['from']) +" 00:00:00"
            date_to = str(request.form['to']) +" 00:00:00"
            try:
                [conn,cur] = connect_db()
                command = f"SELECT  b.id, m.name, s.language, b.date_time, u.email, b.seats,b.total, b.sgst,b.cgst,b.grand_total \
                            FROM bill b\
                            LEFT JOIN  show_list s ON b.show_id = s.id \
                            LEFT JOIN movie_list m ON s.movie_id = m.id \
                            LEFT JOIN user u ON u.id = b.user_id \
                            WHERE b.date_time between '{date_from}' AND '{date_to}'\
                            ORDER BY b.date_time DESC"
                cur.execute(command)
                data = cur.fetchall()
                cur.execute(f"SELECT sum(total),sum(sgst),sum(cgst), sum(grand_total) FROM bill WHERE date_time between '{date_from}' AND '{date_to}'")
                ttl = cur.fetchone()
                return render_template("/admin/bill/show.html", data = data, ttl = ttl)
            finally:
                conn.close()

    else:
        return redirect(url_for('login'))


@admin.route('/admin/staff/show')
def staff_show():
    if session.get('login') and session.get('login_type') == 'admin':
        try:
            [conn,cur] = connect_db()
            command = f"SELECT  u.id,u.firstname,u.lastname,u.email, c.cash\
                        FROM user u\
                        LEFT JOIN (SELECT user_id , sum(amount) cash \
                                    FROM cash \
                                    WHERE Date(time) = CURDATE() \
                                    GROUP BY user_id  ) c ON c.user_id = u.id\
                        WHERE u.user_type = 'staff' OR u.user_type = 'admin'" 
            cur.execute(command)
            data = cur.fetchall()
            return render_template("/admin/staff/show.html", data = data)
        finally:
            conn.close()
    else:
        return redirect(url_for('login'))

@admin.route('/admin/staff/remove/<id>', methods = ["GET","POST"] )
def staff_remove(id):
    if session.get('login') and session.get('login_type') == 'admin':
        try:
            [conn,cur] = connect_db()
            command = f"UPDATE `user` SET user_type = 'user' WHERE id={id}"
            cur.execute(command)
            return redirect(url_for('admin.staff_show'))
        finally:
            conn.close()
    else:
        return redirect(url_for('login'))

@admin.route('/admin/staff/add', methods = ["GET","POST"])
def staff_add():
    if session.get('login') and session.get('login_type') == 'admin':
        if request.method == "GET":
            return render_template('/admin/staff/add.html',message = None)
        else:
            user_id = request.form['user_id']
            try:
                [conn,cur] = connect_db()
                command = f"SELECT id FROM `user` WHERE email ='{user_id}'" 
                cur.execute(command)
                uid = cur.fetchone()
                if len(uid) == 1:
                    command = f"UPDATE `user` SET user_type = 'staff' WHERE email ='{user_id}'" 
                    cur.execute(command)
                    return redirect(url_for('admin.staff_show'))
                else: 
                    return render_template('/admin/staff/add.html',message = True)
            finally:
                conn.close()
    else:
        return redirect(url_for('login'))
