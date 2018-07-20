from flask import Flask, render_template, request, escape
from vsearch import search4letters

from DBcm import UseDatabase, ConnectionError, CredentialsError
from checker import check_logged_in

from threading import Thread

app = Flask(__name__)

app.config['dbconfig'] = { 'host': '127.0.0.1',
                           'user': 'vsearch',
                           'password': 'vsearchpasswd',
                           'database': 'vsearchlogDB', }

@app.route('/login')
def do_login() -> str:
    session['logged_in'] = True
    return 'You are now logged in.'

@app.route('/logout')
def do_logout() -> str:
    session.pop('logged_in')
    return 'You are now logged out.'

def log_request(req: 'flask_request', res: str) -> None:
    """Журналирует веб-запрос и возвращаемые результаты"""
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """insert into log
                  (phrase, letters, ip, browser_string, results)
                  values
                  (%s, %s, %s, %s, %s)"""
        cursor.execute(_SQL, (req.form['phrase'],
                              req.form['letters'],
                              req.remote_addr,
                              req.user_agent.browser,
                              res, ))

@app.route('/search4', methods=['POST'])
def do_search() -> 'html':
    """Извлекает данные из запроса; выполняет поиск; возвращает результаты."""
    phrase = request.form['phrase']
    letters = request.form['letters']
    title = 'Here are your results:'
    results = str(search4letters(phrase,letters))
    try:
        t = Thread(target=log_request, args=(request, results))
        t.start()
    except Exception as err:
        print('*****Logging failed with this error', str(err))
    return render_template('resutls.html',
                            the_phrase = phrase,
                            the_letters = letters,
                            the_title = title,
                            the_results = results,)

@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    """Выводит HTML-форму."""
    return render_template('entry.html',

                           the_title='Welcome to search4letters on the web!')

@app.route('/viewlog')
@check_logged_in
def viem_the_log() -> 'html':
    """Выводит содержимое файла журнала в виде HTML-таблицы"""
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = """select phrase, letters, ip, browser_string, results
                      from log"""
            cursor.execute(_SQL)
            contens = cursor.fetchall() #fetchall возвращает как список кортежей           
        # raise Exception("Some unkniwn exception")
        titles = ('Phrase', 'Letters', 'Remote_addr', 'User_agent', 'Results')
        return render_template('viewlog.html',
                           the_tltle = 'Viem Log',
                           the_row_titles = titles,
                           the_data = contens,)
    except ConnectionError as err:
        print('Is your database switched on? Error:', str(err))
    except CredentialsError as err:
        print('User-id/Password issues. Error:', str(err))
    except SQLError as err:
        print('Is your query correct? Error:', str(err)) 
    except Exception as err:
        print('Something went wrong:', str(err))
    return 'Error'

app.secret_key = 'YouWillNeverGuessMySecretKey'

if __name__ == '__main__': #если приложение выполняется на локалке, то применить app.run()
    app.run(debug=True)


