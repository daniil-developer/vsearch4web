from flask import Flask, render_template, request, escape

from vsearch import search4letters

app = Flask(__name__)

import mysql.connector

def log_request(req: 'flask_request', res: str) -> None:
    """Журналирует веб-запрос и возвращаемые результаты"""
    
    dbconfig = { 'host': '127.0.0.1',
                 'user': 'vsearch',
                 'password': 'vsearchpasswd',
                 'database': 'vsearchlogDB', }

    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()
    
    _SQL = """insert into log
              (phrase, letters, ip, browser_string, results)
              values
              (%s, %s, %s, %s, %s)"""
    cursor.execute(_SQL, (req.form['phrase'],
                          req.form['letters'],
                          req.remote_addr,
                          req.user_agent.browser,
                          res, ))
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/search4', methods=['POST'])
def do_search() -> 'html':
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
    return render_template('entry.html',
                           the_title='Welcome to search4letters on the web!')

@app.route('/viewlog')
def viem_the_log() -> 'html':
    contens = []
    with open('vsearch.log') as log:
        for line in log:
            contens.append([])
            for item in line.split('|'): #разбить строку (по вертикальной черте) а затем обработать каждый эелемент в получаеннмо списке
                contens[-1].append(escape(item))
    titles = ('Form Data', 'Remote_addr', 'User_agent', 'Results')
    return render_template('viewlog.html',
                           the_tltle = 'Viem Log',
                           the_row_titles = titles,
                           the_data = contens,)
    
if __name__ == '__main__': #если приложение выполняется на локалке, то применить app.run()
    app.run(debug=True)
