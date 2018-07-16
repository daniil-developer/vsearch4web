from flask import Flask, render_template, request, escape
from vsearch import search4letters

from DBcm import UseDatabase

app = Flask(__name__)

app.config['dbconfig'] = { 'host': '127.0.0.1',
                           'user': 'vsearch',
                           'password': 'vsearchpasswd',
                           'database': 'vsearchlogDB', }

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
    log_request(request, results)
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
def viem_the_log() -> 'html':
    """Выводит содержимое файла журнала в виде HTML-таблицы"""
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """select phrase, letters, ip, browser_string, results
                  from log"""
        cursor.execute(_SQL)
        contens = cursor.fetchall() #fetchall возвращает как список кортежей           
    titles = ('Phrase', 'Letters', 'Remote_addr', 'User_agent', 'Results')
    return render_template('viewlog.html',
                           the_tltle = 'Viem Log',
                           the_row_titles = titles,
                           the_data = contens,)
    
if __name__ == '__main__': #если приложение выполняется на локалке, то применить app.run()
    app.run(debug=True)
