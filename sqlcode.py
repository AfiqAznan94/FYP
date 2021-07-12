import pymysql

db = pymysql.connect(host='127.0.0.1',user='root',passwd='', database='unimaplab')

def fetchname(ID):
    cursor = db.cursor()
    cursor.execute("select Name from login where ID = "+ID)
    results= cursor.fetchone()
    return results

def insertnewuser(data):
    cursor = db.cursor()
    sql = "insert into login (ID, Name, Password, Priv) VALUES (%s, %s, %s, %s)"
    val = (data)
    results = cursor.execute(sql,val)
    db.commit()
    return results

def fetchpass(ID):
    cursor = db.cursor()
    cursor.execute("select Password,Name from login where ID = "+ID)
    results= cursor.fetchone()
    return results

