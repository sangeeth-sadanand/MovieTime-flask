import mysql.connector as mysql
from flask import url_for
db_name = 'movie_time_db'


def connect_db() :
    """Create connection to database."""
    try:
        conn = mysql.connect(host = 'localhost', user = 'root', passwd = '', database = db_name)
        try:
            cur = conn.cursor()
            return[conn,cur]
        except Exception as e:
            print('\nException occurred\n' + str(e) )
            conn.close()
    except Exception as e:
        print('\nError occurred while connecting please\n' + str(e) )
    
###################################################  USER DATA MANUPULATION ################################
def get_user_data(sel = '*', where = None ):
    [conn, cur] = connect_db()
    try:
        if where == None :
            where = ""
        else:
            where = 'WHERE '+ where
        print(f"SELECT {sel} from user {where}")
        cur.execute(f"SELECT {sel} from user {where}")
        return cur.fetchall()
    finally:
        conn.close()


def insert_user_data(data):
    [conn,cur] = connect_db()
    try:
        cur.execute(f"INSERT INTO `user` ( `firstname`, `lastname`, `email`, `password`, `user_type`) \
            VALUES ('{data['firstname']}', '{data['lastname']}', '{data['email']}', '{data['password']}', '{data['type']}')")
        conn.close()
    except Exception as e:
        print('\nException occurred\n' + str(e) )
        conn.close()
############################################### MOVIE DATA MANUPULATION ##########################
def get_movie_data(sel = '*', where = None):
    [conn, cur] = connect_db()
    try:
        if where == None :
            where = ""
        else:
            where = 'WHERE '+ where
        cur.execute(f"SELECT {sel} from movie {where}")
        return cur.fetchall()
    finally:
        conn.close()


def insert_movie_data(data: dict):
    [conn,cur] = connect_db()
    try:
        cur.execute(f"INSERT INTO movie(name, languages, genes, run_time,\
        rating, now_showing, poster_url, release_date, description) \
        VALUES('{data['name']}', '{data['languages']}', '{data['genes']}', '{data['runtime']}',\
        '{data['rating']}', '{data['status']}', '{data['filename']}', '{data['release_date']}', '{data['desc']}')")
        conn.close()
    except Exception as e:
        print('\nException occurred\n' + str(e) )
        conn.close()


def update_movie_data(data):
    [conn, cur] = connect_db()
    try:
        cur.execute(f"UPDATE movie \
            SET name = '{data['name']}', languages = '{data['languages']}', genes ='{data['genes']}',\
            run_time = '{data['runtime']}', rating ='{data['rating']}', now_showing ='{data['status']}',\
            poster_url = '{data['filename']}', release_date ='{data['release_date']}', description = '{data['desc']}' \
            WHERE id ={data['id']}")
        conn.close()
    except Exception as e:
        print('\nException occurred\n' + str(e) )
        conn.close()

def delete_movie_data(id):
    [conn, cur] = connect_db()
    try:
        cur.execute(f"DELETE FROM movie WHERE id = {id}")
        conn.close()
    except Exception as e:
        print('\nException occurred\n' + str(e) )
        conn.close()

######################################################################## Show Table ################################
def get_show_data(sel="*",where = None):
    [conn, cur] = connect_db()
    try:
        if where == None :
            where = ""
        else:
            where = 'WHERE '+ where
        cur.execute(f"SELECT {sel} from show_db {where}")
        return cur.fetchall()
    finally:
        conn.close()

def insert_show_data(data: dict):
    [conn,cur] = connect_db()
    try:
        veri = get_show_data(sel = 'id', where = f"('{data['start_time']}' between `from_time` and `to_time`\
        OR '{data['end_time']}' between from_time and to_time\
        OR from_time between '{data['start_time']}' and '{data['end_time']}'\
        OR to_time between '{data['start_time']}' and '{data['end_time']}')\
        AND screen = {data['screen']} AND date = '{data['date']}'")
        if len(veri)==0:
            command = f"INSERT INTO `show_db` \
                (`screen`, `movie_id`, `date`, `language`, `from_time`,\
                `runtime`, `breaktime`, `gaptime`, `to_time`, `platinum`, `gold`, `silver`)\
                VALUES ('{data['screen']}','{data['movie']}','{data['date']}','{data['languages']}','{data['start_time']}'\
                ,'{data['run_time']}','{data['break_time']}','{data['gap_time']}','{data['end_time']}'\
                ,'{data['plat']}','{data['gold']}','{data['silv']}')"
            print(command)
            cur.execute(command)
            conn.close()
        else:
            print('Error occurred')
    except Exception as e:
        print('\nException occurred\n' + str(e) )
        conn.close()

def get_show_data_join_movie(sel = "*", where = None):
    [conn, cur] = connect_db()
    try:
        if where == None :
            where = ""
        else:
            where = 'WHERE '+ where
        cur.execute(f"SELECT {sel} FROM show_db s LEFT JOIN movie m ON s.movie_id=m.id {where} ORDER BY `from_time` ASC")
        return cur.fetchall()
    finally:
        conn.close()

def update_show_data(data:dict):
    [conn,cur] = connect_db()
    try:
        start_time = data['start_time']
        end_time = data['end_time']
        veri = get_show_data(sel = 'id', where = f"('{start_time}' between `from_time` and `to_time`\
        OR '{end_time}' between from_time and to_time\
        OR from_time between '{start_time}' and '{end_time}'\
        OR to_time between '{start_time}' and '{end_time}')\
        AND screen = '{data['screen']}' AND date = '{data['date']}' AND id <> {data['id']}")
        if len(veri)==0:
            command = f"UPDATE `show_db` SET \
                `screen`= '{data['screen']}', `movie_id` = '{data['movie']}', `date` = '{data['date']}',\
                `language` = '{data['languages']}', `from_time` = '{data['start_time']}', `runtime` = '{data['run_time']}', \
                `breaktime` = '{data['break_time']}', `gaptime` ='{data['gap_time']}', `to_time`= '{data['end_time']}',\
                `platinum`= '{data['plat']}', `gold` ='{data['gold']}', `silver` ='{data['silv']}'\
                WHERE id = {data['id']}"
            print(command)
            cur.execute(command)
            conn.close()
        else:
            print('Error occurred')
    except Exception as e:
        print('\nException occurred\n' + str(e) )
        conn.close()

def delete_show_data():
    [conn, cur] = connect_db()
    try:
        cur.execute(f"DELETE FROM show_db WHERE id = {id}")
        conn.close()
    except Exception as e:
        print('\nException occurred\n' + str(e) )
        conn.close()


####################################################### SEAT ############################################################

def get_seat_data(sel="*",where = None):
    [conn, cur] = connect_db()
    try:
        if where == None :
            where = ""
        else:
            where = 'WHERE '+ where
        cur.execute(f"SELECT {sel} from seat {where}")
        return cur.fetchall()
    finally:
        conn.close()



########################################################## SCREEN ########################################################
def get_screen_data(no):
    import json
    try :
        with open('static/screen/screen'+str(no)+'.json','r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        data = {}
        print('Error occurred json file')
        return data