from flask import Flask, render_template, request, redirect, url_for
from flask_sockets import Sockets
from werkzeug.utils import secure_filename
import os, base64
import face_recognition as fr

UPLOAD_FOLDER = "media"
ALLOWED_EXT = set(['jpg', 'jpeg', 'png', 'txt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
sockets = Sockets(app)

@app.route("/")
def index():
	if 'previous' in request.args:
		return render_template('index.html',
			previous=request.args.get('previous'))
	return render_template('index.html')

@app.route("/search")
def search():
	return render_template('searchresults.html', result=request.args['q'])

@app.route("/detect")
def detect():
	return render_template('face_detect.html')

@app.route("/post", methods=["GET", "POST"])
def post():
	if request.method == "POST":
		if 'file' not in request.files:
			# no file at all
			return redirect(request.url)
		file = request.files['file']
		if file.filename == "":
			# no file selected
			return redirect(request.url)
		if file and allowed_filename(file.filename):
			filename = secure_filename(file.filename)
			# file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return redirect(url_for('post'))
	return render_template('post.html')

@sockets.route('/get_message')
def get_message(ws):
	while True:
		message = ws.receive()
		# raw = message.decode('utf8')
		head = "data:image/jpeg;base64,"
		if(head in message):
			print("1")
			imgdata = base64.b64decode(message[len(head):])
			filename = secure_filename("temp.jpg")
			with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'wb') as imgFile:
				imgFile.write(imgdata)
				generate_face_encoding(filename)
		else:
			print("0")
			
		# assert(raw.startsWith(head))
		# print(message)

def allowed_filename(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def generate_face_encoding(filename):
	img = fr.load_image_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	enc_list = fr.face_encodings(img)
	if len(enc_list) > 0:
		u_encoding = enc_list[0]
		print(u_encoding)
	else:
		print("Could not generate encoding")

if __name__=="__main__":
	# app.run(debug=True)
	from gevent import pywsgi
	from geventwebsocket.handler import WebSocketHandler
	server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
	server.serve_forever()