from flask import Blueprint,Flask, render_template,session,request,abort,redirect,url_for,flash,get_flashed_messages
from werkzeug.utils import secure_filename
from datetime import datetime as dt

from modules.Db_functions import *


user = Blueprint('user', __name__)

@user.route('/bookticket/<show_id>', methods = ["GET", 'POST'])
def bookticket_scr(show_id):
    if session.get('login'):
        if request.method == 'GET' :
            screen = get_show_data(sel='screen,language,movie_id,from_time,to_time,date,platinum,gold,silver',where=f"id = {show_id}")[0]
            data = {'screen':screen[0],'language':screen[1],'plat': screen[-3],
            'gold': screen[-2],'silv':screen[-1],'time': str(screen[3])+'-'+str(screen[4]),
            'date':str(screen[5])}
            screen_data = get_screen_data(screen[0])
            data['movie_name'] = get_movie_data(sel='name',where =f"id = '{screen[2]}'")[0][0]
            data['show_id'] =show_id
            #print('*'*25, data , '*'*25, sep = '\n')
            unavilable_seats = get_seat_data(sel = "seat_no",where = f"show_id = {show_id}")
            unavilable_seats = list(map(lambda x:x[0],unavilable_seats))
            session['ticket_data'] = data
            return render_template('/bookticket/seat_query.html',data = data, screen_data = screen_data, unavilable_seats = unavilable_seats)
        else:
            temp = session['ticket_data']
            temp['selected_seats'] = request.form['selected_seats']
            seats = temp['selected_seats'].split(',')
            screen_data = get_screen_data(temp['screen'])
            temp['no_of_seats'] = len(seats)
            plat = screen_data['plat']
            gold = screen_data['gold']
            silv = screen_data['silv']
            no_plat,no_gold,no_silv = 0,0,0
            for seat in seats:
                if seat[0] in plat:
                    no_plat += 1
                elif seat[0] in gold:
                    no_gold += 1
                else:
                    no_silv += 1

            co_plat = no_plat * int(session.get('ticket_data')['plat'])
            co_gold = no_gold * int(session.get('ticket_data')['gold'])
            co_silv = no_silv * int(session.get('ticket_data')['silv'])
            tsum = co_plat + co_gold + co_silv
            gst = round(0.18 * tsum,2)
            gsum = tsum +gst
            session['bill_data'] = [[no_plat, session.get('ticket_data')['plat'],co_plat],
            [no_gold, session.get('ticket_data')['gold'],co_gold],
            [no_silv, session.get('ticket_data')['silv'],co_silv],[tsum,gst,gsum]]
            session['ticket_data'] = temp
            if session.get('login_type') == "user":
                return redirect(url_for('user.quote'))
            else:
                return redirect(url_for('user.staff_quote'))
    else:
        return redirect(url_for('login'))



@user.route('/ajax/seat_select')
def ajax_seat_selected():
    show_id = request.args['show_id']
    seat = request.args['seat']
    [conn,cur] = connect_db()
    try:
        cur.execute('LOCK TABLE seat WRITE')
        cur.execute(f"SELECT * FROM seat WHERE show_id = {show_id} AND seat_no = '{seat}'")
        tbl = cur.fetchall()
        print(len(tbl))
        if len(tbl) == 0:
            cur.execute(f"INSERT INTO seat(`show_id`, `seat_no`, `temp_allocated`, `user_id` ) \
                VALUES ('{show_id}','{seat}', '{1}','{session.get('login_id')}')")
            return 'true'
        else:
            return 'false'
    finally:
        cur.execute('UNLOCK TABLES')
        conn.close()

@user.route('/ajax/seat_unselect')
def ajax_seat_unselect():
    show_id = request.args['show_id']
    seat = request.args['seat']
    [conn,cur] = connect_db()
    try:
        cur.execute('LOCK TABLE seat WRITE')
        cur.execute(f"DELETE FROM seat WHERE show_id = '{show_id}' AND seat_no = '{seat}'")
        return 'true'
    finally:
        cur.execute('UNLOCK TABLES')
        conn.close()

###############################################################################################################3
@user.route('/bookticket/quote/', methods = ["GET", 'POST'])
def quote():
    if session.get('login'):
        if request.method == "GET":
            if session.get('ticket_data'):
                return render_template("/bookticket/staff_quote.html")
            else:
                return redirect(url_for('home'))
        else:
            cc_name = request.form['card_holder_name']
            cc_number = request.form['card_number']
            expiry = request.form['expiration']
            cvv = request.form['cvv']
            amount = session.get('bill_data')[3][2]
            print(f"SELECT transfer_money('{cc_number}','{cc_name.upper()}',{cvv},'{expiry}','1000100010001000',{amount})")
            try:
                conn = mysql.connect(host = 'localhost', user = 'root', passwd = '', database = 'mt_bank')
                try:
                    cur = conn.cursor()
                    cur.execute(f"SELECT transfer_money('{cc_number}','{cc_name.upper()}',{cvv},'{expiry}','1000100010001000',{amount})")
                    transaction = cur.fetchone()
                    if transaction[0] == 'TRANSFER SUCCESSFUL':
                        session['cc_number'] = cc_number;
                        return redirect(url_for('user.transaction_successful'))
                    else:
                        return redirect(url_for('user.transaction_failed',failed_id=transaction[0]))
                except Exception as e:
                    print('\nException occurred\n' + str(e) )
                    return redirect(url_for('home'))
            except Exception as e:
                print('\nError occurred while connecting please\n' + str(e) )
                return redirect(url_for('home'))
            finally:
                    conn.close()
                
    else:
        return redirect(url_for('home'))

###############################################################################################################3
@user.route('/bookticket/quote/', methods = ["GET", 'POST'])
def staff_quote():
    if session.get('login'):
        if request.method == "GET":
            if session.get('ticket_data'):
                return render_template("/bookticket/quote.html")
            else:
                return redirect(url_for('home'))
        else:
            cc_name = request.form['card_holder_name']
            cc_number = request.form['card_number']
            expiry = request.form['expiration']
            cvv = request.form['cvv']
            amount = session.get('bill_data')[3][2]
            print(f"SELECT transfer_money('{cc_number}','{cc_name.upper()}',{cvv},'{expiry}','1000100010001000',{amount})")
            try:
                conn = mysql.connect(host = 'localhost', user = 'root', passwd = '', database = 'mt_bank')
                try:
                    cur = conn.cursor()
                    cur.execute(f"SELECT transfer_money('{cc_number}','{cc_name.upper()}',{cvv},'{expiry}','1000100010001000',{amount})")
                    transaction = cur.fetchone()
                    if transaction[0] == 'TRANSFER SUCCESSFUL':
                        session['cc_number'] = cc_number;
                        return redirect(url_for('user.transaction_successful'))
                    else:
                        return redirect(url_for('user.transaction_failed',failed_id=transaction[0]))
                except Exception as e:
                    print('\nException occurred\n' + str(e) )
                    return redirect(url_for('home'))
            except Exception as e:
                print('\nError occurred while connecting please\n' + str(e) )
                return redirect(url_for('home'))
            finally:
                    conn.close()
                
    else:
        return redirect(url_for('home'))

@user.route('/bookticket/cash')
def cash():
    amount = session.get('bill_data')[3][2]
    try:
        [conn,cur] = connect_db()
        try:
            cur.execute("")
            cur.execute('LOCK TABLES seat WRITE, bill WRITE, cash WRITE')
            selected_seats = session.get('ticket_data')['selected_seats']
            show_id = session.get('ticket_data')['show_id']
            check = True
            for seat in selected_seats.split(','):
                cur.execute(f"SELECT * FROM seat WHERE show_id = {show_id} AND seat_no = '{seat}'")
                tbl = cur.fetchone()
                if tbl:
                    if tbl[3] != session.get('login_id'):
                        check = False
            if check :
                for seat in selected_seats.split(','):
                    print(f"UPDATE `seat` SET `temp_allocated` = 0 WHERE show_id = {show_id} AND seat_no = '{seat}'")
                    cur.execute(f"UPDATE `seat` SET `temp_allocated` = 0 WHERE show_id = {show_id} AND seat_no = '{seat}'")
                no_of_seats=str(session.get('bill_data')[0][0])+","+str(session.get('bill_data')[1][0])+","+str(session.get('bill_data')[2][0])
                cur.execute("SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'movie_time_db' AND TABLE_NAME = 'bill'")
                index=cur.fetchone()[0]
                cur.execute(f"INSERT INTO `bill`(id,`show_id`, `user_id`, `no_of_seat`,`seats`, `total`, `cgst`, `sgst`, `grand_total`) \
                    VALUES ({index},{show_id},{session.get('login_id')},'{no_of_seats}','{selected_seats}',{session.get('bill_data')[3][0]},{session.get('bill_data')[3][1]},{session.get('bill_data')[3][1]},{session.get('bill_data')[3][2]})")
                cur.execute(f"INSERT INTO `cash`(`user_id`,`amount`) VALUES ({session.get('login_id')}, {session.get('bill_data')[3][2]})")
                return redirect(url_for('user.print_ticket',id=index))
            else:
                return render_template("/bookticket/session_timeout.html")
        finally:
            conn.close()
    except Exception as e:
        print(e)

@user.route('/bookticket/successful')
def transaction_successful():
    if session.get('cc_number'):
        [conn,cur] = connect_db()
        try:
            cur.execute('LOCK TABLES seat WRITE, bill WRITE')
            selected_seats = session.get('ticket_data')['selected_seats']
            show_id = session.get('ticket_data')['show_id']
            print(session)
            check = True
            for seat in selected_seats.split(','):
                cur.execute(f"SELECT * FROM seat WHERE show_id = {show_id} AND seat_no = '{seat}'")
                tbl = cur.fetchone()
                if tbl:
                    if tbl[3] != session.get('login_id'):
                        check = False
            if check :
                for seat in selected_seats.split(','):
                    cur.execute(f"UPDATE `seat` SET `temp_allocated` = 0 WHERE show_id = {show_id} AND seat_no = '{seat}'")
                    no_of_seats=str(session.get('bill_data')[0][0])+","+str(session.get('bill_data')[1][0])+","+str(session.get('bill_data')[2][0])
                    cur.execute("SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'movie_time_db' AND TABLE_NAME = 'bill'")
                    index=cur.fetchone()[0]
                    cur.execute(f"INSERT INTO `bill`(id,`show_id`, `user_id`, `no_of_seat`,`seats`, `total`, `cgst`, `sgst`, `grand_total`) \
                         VALUES ({index},{show_id},{session.get('login_id')},'{no_of_seats}','{selected_seats}',{session.get('bill_data')[3][0]},{session.get('bill_data')[3][1]},{session.get('bill_data')[3][1]},{session.get('bill_data')[3][2]})")
                    return redirect(url_for('user.print_ticket',id=index))
            else:
                return redirect(url_for('user.session_timeout'))

        finally:
            cur.execute('UNLOCK TABLES')
            conn.close()

@user.route('/ticket/<id>')
def ticket(id):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    [conn,cur] = connect_db()
    cur.execute(f"SELECT * FROM bill where id={id}")
    bill = cur.fetchone()
    user_id = bill[2]
    cur.execute(f"SELECT email FROM user where id={user_id}")
    email=cur.fetchone()[0]
    mail_content = f"Your Ticket id is: {id} . Please collect your ticket from ticket counter." 
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
    return render_template("/bookticket/emailinfo.html") 

@user.route('/transaction_failed/<failed_id>')
def transaction_failed(failed_id):
    return render_template("/bookticket/transaction_failed.html",failed_id =failed_id)

@user.route('/session_timeout')
def session_timeout():
    try:
        conn = mysql.connect(host = 'localhost', user = 'root', passwd = '', database = 'mt_bank')
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT transfer_money('1000100010001000','MOVIE TIME',123,'02-25',{session['cc_number']},{session.get('bill_data')[3][2]})")
            transaction = cur.fetchone()
            return render_template("/bookticket/session_timeout.html")
        except Exception as e:
            print('\nException occurred\n' + str(e) )
            return redirect(url_for('home'))
    except Exception as e:
        print('\nError occurred while connecting please\n' + str(e) )
        return redirect(url_for('home'))
    finally:
            conn.close()


@user.route('/book_ticket/print/<id>')
def print_ticket(id):
    [conn,cur] = connect_db()
    try:
        command = f"SELECT  m.name,s.date, s.from_time, b.grand_total, s.screen,b.seats,b.id \
                    FROM bill b\
                    LEFT JOIN  show_list s ON b.show_id = s.id \
                    LEFT JOIN movie_list m ON s.movie_id = m.id \
                    WHERE b.id = {id} \
                    ORDER BY b.date_time DESC"
        cur.execute(command)
        data = cur.fetchall()
        return render_template("/bookticket/print_ticket.html", data = data)
    finally:
        conn.close()
@user.route('/book_ticket/print_ticket', methods = ['POST', 'GET'] )
def staff_print():
    if request.method == "GET":
        return render_template("/bookticket/staff_print_ticket.html", data = None )
    else:
        id = request.form['id']
        [conn,cur] = connect_db()
        try:
            command = f"SELECT  m.name,s.date, s.from_time, b.grand_total, s.screen,b.seats,b.id \
                        FROM bill b\
                        LEFT JOIN  show_list s ON b.show_id = s.id \
                        LEFT JOIN movie_list m ON s.movie_id = m.id \
                        WHERE b.id = {id} \
                        ORDER BY b.date_time DESC"
            cur.execute(command)
            data = cur.fetchall()
            return render_template("/bookticket/staff_print_ticket.html", data = data)
        finally:
            conn.close()