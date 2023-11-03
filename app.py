import os
import sys
import time
import openai
import configparser
import sqlite3

dir_path = os.path.abspath(os.getcwd())

utils_path = dir_path + "/src/app_utils"
src_path = dir_path + "/src"
sys.path.append(utils_path)
sys.path.append(src_path)

from flask import Flask, render_template, request, redirect, url_for, g
import application_utils as au

COMPLETIONS_MODEL = "gpt-3.5-turbo"
EMBEDDING_MODEL = "text-embedding-ada-002"
config_dir = utils_path
config = configparser.ConfigParser()
config.read(os.path.join(config_dir, 'gpt_local_config.cfg'))
openai.api_key = config.get('token', 'GPT_TOKEN')

# Specify the path to db file
db_name = 'caNanoData_Public.db'

COMPLETIONS_API_PARAMS = {
    # We use temperature of 0.0 because it gives
    # the most predictable, factual answer.
    "temperature": 0.0,
    "max_tokens": 800,
    "model": "gpt-3.5-turbo"
}

app = Flask("caNanoLibrarian")

# Set the passcode for authentication
PASSCODE_auth = "caNanoLibrarian_DEMO_wkrh_6152023*"

# Define a variable to track if the user is authenticated
authenticated = False
last_activity_time = 0

# Timeout duration in seconds
timeout_duration = 5 * 60

# Session Length
session_duration = 30 * 60


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('caNanoData_Public.db')
    return db


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.template_filter('nl2br')
def nl2br_filter(s):
    return s.replace('\n', '<br>')


@app.route('/', methods=['GET', 'POST'])
def index():
    global authenticated, last_activity_time, login_time

    if not authenticated:
        return redirect(url_for('login'))

    # Check for timeout
    current_time = time.time()
    if current_time - last_activity_time > timeout_duration:
        authenticated = False
        return redirect(url_for('login'))

    # Check for session timeout
    if current_time - login_time > session_duration:
        authenticated = False
        return redirect(url_for('login'))

    # Update last activity time
    last_activity_time = current_time
    connection = get_db()

    user_input = ""
    # processed_input = None
    if request.method == 'POST':
        user_input = request.form['user_input']
        result_df, query = au.custom_query(
                        user_input, connection,
                        GPT4=True,
                        print_prompt=False,
                        print_query=True,
                        print_time=False
                    )
        return render_template(
            'index.html',
            processed_input=result_df.to_html(
                classes='dataframe custom-style',
                index=False),
            source_sections=query,
            user_input=user_input,
            authenticated=authenticated)

    return render_template('index.html', authenticated=authenticated)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global authenticated, last_activity_time, login_time

    if request.method == 'POST':
        password = request.form['passcode']
        if password == PASSCODE_auth:
            authenticated = True
            last_activity_time = time.time()
            login_time = time.time()
            return redirect(url_for('index'))
        else:
            return render_template('login.html', message='Incorrect password')

    return render_template('login.html')


@app.route('/logout')
def logout():
    global authenticated
    authenticated = False
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
