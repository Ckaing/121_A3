from flask import Flask, render_template, request

#TODO replace with actual search
from tmp_search_result import process_query

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['user_query'] # Get data from the form
        results = process_query(query)
        return render_template('result.html', results=results)
    return render_template('index.html')

# run python web_interface.py
if __name__ == '__main__':
    app.run(debug=True)
    # app.run(debug=True, port=5001) # this is bc i had problem with port=5000, but by default it should work