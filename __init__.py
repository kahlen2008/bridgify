from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html', active_page='home')

@app.route('/journal')
def journal():
    return render_template('journal.html', active_page='journal')


if __name__=='__main__':
    app.run()