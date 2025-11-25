from flask import Flask, render_template, request
import time

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from query import query as process_query
from query import extract_terms


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['user_query']
        start_time = time.time()
        urls = process_query(extract_terms(query))
        time_elapsed = time.time() - start_time
        results = {'urls': urls, 'time':time_elapsed, 'query':query}
        return render_template('result.html', results=results)
    return render_template('index.html')

# run python web_interface.py
if __name__ == '__main__':
    app.run(debug=True)
    # app.run(debug=True, port=5001) # this is bc i had problem with port=5000, but by default it should work