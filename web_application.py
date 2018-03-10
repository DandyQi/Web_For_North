import os
import time
from flask import Flask, render_template, send_from_directory, request, jsonify
from match_record import MatchRecord
app = Flask(__name__)

UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/office/match_record')
def match_record():
	return render_template('upload.html')

@app.route('/api/upload', methods = ['POST'], strict_slashes = False)
def api_upload():
	file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
	if not os.path.exists(file_dir):
		os.makedirs(file_dir)
	f = request.files['myfile']
	if f and allowed_file(f.filename):
		fname = f.filename
		ext = fname.rsplit('.', 1)[1]
		unix_time = int(time.time())
		new_filename = str(unix_time)+'.'+ext
		f.save(os.path.join(file_dir, new_filename))
		try:
			mr = MatchRecord(os.path.join(file_dir, new_filename))
			mr.main()
			return render_template('download.html')
		except Exception as e:
			raise e
			return jsonify({'code': 2, 'msg': str(e)})
	else:
		return jsonify({'code': 1, 'msg': 'failed!'})

@app.route('/api/download', methods = ['GET'])
def api_download():
	dirpath = './result'
	return send_from_directory(dirpath, 'output.txt', as_attachment = False)

if __name__ == '__main__':
	app.run(host = '0.0.0.0')
