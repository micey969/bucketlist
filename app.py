import json
import time
from flask import Flask, flash, render_template, request, jsonify, session, redirect
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash


mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'secret key'
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Ssps@1109-1517'
app.config['MYSQL_DATABASE_DB'] = 'Bucketlist'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)



@app.route("/")
def main():
	return render_template('index.html')


@app.route('/SignUp')
def showSignUp():
	return render_template('signup.html')


@app.route('/SignUp', methods=['POST'])
def SignUp():
	name = request.form.get('inputName')
	email =  request.form.get('inputEmail')
	password = request.form.get('inputPassword')
	
	if request.form == None:
		return jsonify({'message':'Required fields are missing.'}), 400
	else:
		try:
			conn = mysql.connect()
			cursor = conn.cursor()
			password = generate_password_hash(password)

			# forgetting about the stored procedure for now
			# cursor.callproc('sp_createUser', (name, email, password))
			cursor.execute("SELECT * FROM user WHERE user_username = %s", (email))
			data = cursor.fetchall()

			if len(data) is not 0:
				# can't seem to get flash to show up
				# flash("That username is already taken...")
				message = "That username is already taken..."
				return render_template('signup.html',message = message)

			else:  
				cursor.execute("INSERT INTO user (user_name, user_username, user_password) VALUES (%s,%s,%s)",(name, email, password))
				conn.commit()
				# flash("User successfully created!!")
				message = "User successfully created!!"
				return render_template('index.html',message = message)
	
		except Exception as e:
			conn.rollback()
			return render_template('error.html',error = str(e))
		finally:
			cursor.close() 
			conn.close()	


@app.route('/Login')
def showLogin():
	return render_template('login.html')


@app.route('/Login', methods=['POST'])
def Login():
	username =  request.form.get('inputEmail')
	password = request.form.get('inputPassword')

	if request.form == None:
		return jsonify({'message':'Required fields are missing.'}), 400
	else:
		try:
			conn = mysql.connect()
			cursor = conn.cursor()

			# forgetting about the stored procedure for now
			# cursor.callproc('sp_login', (username, password))
			cursor.execute("SELECT * FROM user WHERE user_username = %s", (username))
			data = cursor.fetchall()

			if len(data) is not 0:
				if check_password_hash(str(data[0][3]), password):
					session['user'] = data[0][0]
					session['name'] = data[0][1]
					return redirect('/User')
				else:
					return render_template('error.html',error = 'Wrong Email address or Password.')
			else:
				return render_template('error.html',error = 'Wrong Email address or Password.')
		except Exception as e:
			conn.rollback()
			return render_template('error.html',error = str(e))
		finally:
			cursor.close()
			conn.close()


@app.route('/User')
def userHome():
	if session.get('user'):
		username = session.get('name')
		return render_template('userhome.html',name = username)
	else:
		return render_template('error.html',error = 'Unauthorized Access')


@app.route('/Logout')
def logout():
    session.pop('user',None)
    return redirect('/')

if __name__ == "__main__":
	app.run(debug=True,
		threaded=True,
		host='0.0.0.0',
		port=5000)