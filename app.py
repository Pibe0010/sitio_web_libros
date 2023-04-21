import os 
from flask import Flask
from flask import render_template, request,redirect, session
from flaskext.mysql import MySQL
from datetime import datetime
from flask import send_from_directory
from dotenv import load_dotenv


app=Flask(__name__)
app.secret_key="develoteca"
mysql=MySQL()
load_dotenv()



app.config["MYSQL_DATABASE_HOST"]=(os.getenv('DB_HOST'))
app.config["MYSQL_DATABASE_USER"]=(os.getenv('DB_USER'))
app.config["MYSQL_DATABASE_PASSWORD"]=(os.getenv('DB_PASSWORD'))
app.config["MYSQL_DATABASE_DB"]=(os.getenv('DB_DB'))


mysql.init_app(app)




# Seccion sitios

@app.route('/')
def inicio():
    return render_template('sitio/index.html')


@app.route('/sitio/img/<imagen>')
def imagenes(imagen):
    print(imagen)
    return send_from_directory(os.path.join('templates/sitio/img'),imagen)


@app.route("/css/<archivocss>")
def css_link(archivocss):
    return send_from_directory(os.path.join('templates/sitio/css'),archivocss)


@app.route('/libros')
def libros():

    conexion=mysql.connect()
    cursor= conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")
    libros=cursor.fetchall()
    conexion.commit()
    print(libros)


    return render_template('sitio/libros.html', libros=libros)


@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')


# Seccion admin

@app.route('/admin/')
def admin_index():

    if not 'login' in session:
        return redirect("/admin/login")

    return render_template('admin/index.html')


@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    _usuario=request.form['txtUsuario']
    _password=request.form['txtPassword']
    print(_usuario)
    print(_password)

    if _usuario==(os.getenv('USUARIO')) and _password==(os.getenv('PASS')):
        session["login"]=True
        session["usuario"]="Administrador"
        return redirect("/admin")

    return render_template('admin/login.html', mensaje="Acceso denegado")


@app.route('/admin/cerrar')
def admin_login_cerrar():
    session.clear()
    return redirect('/admin/login')


@app.route('/admin/libros')
def admin_libros():

    if not 'login' in session:
        return redirect("/admin/login")
    
    conexion=mysql.connect()
    cursor= conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")
    libros=cursor.fetchall()
    conexion.commit()
    print(libros)

    return render_template('admin/libros.html', libros=libros)


@app.route('/admin/libros/guardar',methods=['POST'])
def admin_libros_guardar():

    if not 'login' in session:
        return redirect("/admin/login")

    _nombre=request.form['txtNombre']
    _url=request.form['txtURL']
    _archivo=request.files['txtImagen']

    tiempo= datetime.now()
    horaActual=tiempo.strftime('%Y%H%M%S')

    if _archivo.filename!="":
        nuevoNombre=horaActual+"_"+_archivo.filename
        _archivo.save("templates/sitio/img/"+nuevoNombre)

    
    sql="INSERT INTO `libros` (`id`, `nombre`, `imagen`, `url`) VALUES (NULL,%s,%s,%s);"
    datos=(_nombre,nuevoNombre,_url)

    conexion= mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()

    
    print(_nombre)
    print(_url)
    print(_archivo)

    return redirect('/admin/libros')


@app.route('/admin/libros/borrar', methods=['POST'])
def admin_libros_borrar():

    if not 'login' in session:
        return redirect("/admin/login")


    _id=request.form['txtID']
    print(_id)


    conexion=mysql.connect()
    cursor= conexion.cursor()
    cursor.execute("SELECT imagen FROM `libros` WHERE id=%s",(_id))
    libro=cursor.fetchall()
    conexion.commit()
    print(libro)

    if os.path.exists("templates/sitio/img/"+str(libro[0][0])):
        os.unlink("templates/sitio/img/"+str(libro[0][0]))
    
    conexion=mysql.connect()
    cursor= conexion.cursor()
    cursor.execute("DELETE FROM libros WHERE id=%s",(_id))
    conexion.commit()


    return redirect('/admin/libros')





if __name__ =='__main__':
    app.run(debug=True)