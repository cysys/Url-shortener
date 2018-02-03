from math import floor
from flask import Flask, request, render_template, redirect
from sqlite3 import OperationalError
import string, sqlite3
from urllib.parse import urlparse
from string import ascii_lowercase
from string import ascii_uppercase
import base64

app = Flask(__name__)
host = 'localhost:5000'

def table_check():
    create_table = """
        CREATE TABLE WEB_URL(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        URL TEXT NOT NULL
        );
        """
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table)
        except OperationalError:
            pass


# Encoder
def base62(n):
	base = string.digits + ascii_lowercase + ascii_uppercase
	rem = n % 62
	result = base[rem]
	div = floor(n / 62)

	while div:
		rem = div % 62
		div = floor(div / 62)
		result = base[rem] + result

	return result

# Decoder
def base10(n):
	base = string.digits + ascii_lowercase + ascii_uppercase
	l = len(n)
	result = 0
	for i in range(l):
		result = 62 * result + base.find(n[i])

	return result

@app.route('/', methods=['GET','POST'])
def index():
	if request.method == 'POST':
		inUrl = str.encode(request.form.get('url'))
		if urlparse(inUrl).scheme == '':
			url = 'http://' + inUrl
		else:
			url = inUrl
		with sqlite3.connect('urls.db') as conn:
			cursor = conn.cursor()
			res = cursor.execute('INSERT INTO WEB_URL (URL) VALUES (?)',[base64.urlsafe_b64encode(url)])
			encoded_string = base62(res.lastrowid)

		return render_template('index.html', short_url=host + encoded_string)

	return render_template('index.html')

@app.route('/<short_url>')
def redirectToSite(short_url):
	decoded = base10(short_url)
	url = host
	with sqlite3.connect('urls.db') as conn:
		cursor = conn.cursor()
		res = cursor.execute('SELECT URL FROM WEB_URL WHERE ID=?',[decoded])

		try:
			short = res.fetchone()
			if short is not None:
				url = base64.urlsafe_b64decode(short[0])
		except Exception as e:
			print(e)
	return redirect(url)

if __name__ == '__main__':
	table_check()
	app.run(debug=True)
