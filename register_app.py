from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

app.secret_key=""

app.config["MYSQL_HOST"] = "localhost"  #bu kısımları sizin veritabanınız localde veya bulunduğu sunucuya göre doldurunuz ..
app.config["MYSQL_USER"] =  "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "" 
app.config["MYSQL_CURSORCLASS"] = ""

#kullanıcı kayıt formu
class RegisterForm(Form):
    name = StringField("İsim Soyisim",validators=[validators.Length(min = 4,max = 25)])
    username = StringField("Kullanıcı Adı",validators=[validators.Length(min = 4,max = 25)])
    email = StringField("Email",validators=[validators.Email(message="lütfen geçerli bir email adresi giriniz..")])
    password = PasswordField("Parola:",validators=[
        validators.DataRequired(message="lütfen bir parola belirleyiniz"),
        validators.EqualTo(fieldname="confirm",message="parolanız uyuşmuyor"), 

    ])
    confirm = PasswordField("Parola doğrula")

class LoginForm(Form):
    username = StringField("Kullanıcı adını giriniz:")
    password = PasswordField("Parolayı giriniz:")


mysql = MySQL(app)

@app.route("/")
def index():
    return render_template("index.html")
@app.route("/register",methods = ["GET","POST"])
def register():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.hash(form.password.data)

        cursor = mysql.connection.cursor()

        sorgu = "Insert into users(name,email,username,password) VALUES(%s,%s,%s,%s)"

        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()

        cursor.close()
        flash("Başarıyla kayıt oldunuz...","success")
        return redirect(url_for("login"))
    else:
        return render_template("register.html",form = form)
@app.route("/about")
def fonk():   
    return render_template("about.html")
@app.route("/articles")
def article():   
    return render_template("article.html")
@app.route("/logout")
def logout():
    session.clear()  
    flash("Başarıyla çıkış yapıldı","success")  
    return redirect(url_for("login"))
@app.route("/picture")
def picture():   
    return render_template("pictures.html")
@app.route("/login",methods = ["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data

        cursor = mysql.connection.cursor()
            
        sorgu = "Select * From users where username = %s"

        result = cursor.execute(sorgu,(username,))

        if result > 0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("Başarıyla giriş yaptınız","success")

                session["logged_in"] = True
                session["username"] = username

                return redirect(url_for("index"))
            else:
                flash("Parolanızı yanlış girdiniz","danger")
                return redirect(url_for("login"))
            
        else:
            flash("Kullanıcı adı bulunamadı!","danger")
            return redirect(url_for("login"))
    else:
        return render_template("login.html",form = form)

if __name__ == "__main__":
    app.run(debug=True)


