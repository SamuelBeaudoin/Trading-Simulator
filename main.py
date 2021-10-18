#$env:FLASK_APP = "webapp"
#Use that ^ to set up environment variable
import os
from flask import Flask, render_template
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(42)

@app.route('/')
def home():
    con = sqlite3.connect('TradingProgress.db')
    cur = con.cursor()

    cur.execute('SELECT * from stocks')
    everything = cur.fetchall()

    cur.execute('SELECT portfolio FROM stocks ORDER BY week DESC LIMIT 1')
    portfolio = cur.fetchall()

    cur.execute('SELECT balance FROM stocks ORDER BY week DESC LIMIT 1')
    portfolioBalance = cur.fetchall()

    cur.execute('SELECT AVG(percentProfit) FROM stocks')
    averageReturn = cur.fetchall()

    con.close()

    ################################################
    #Portfolio Stocks
    ################################################
    portfolio=str(portfolio)
    portfolio = portfolio.replace("[","").replace("]","").replace("(","").replace(")","").replace(",","").replace("'","")

    ################################################
    #Portfolio Balance
    ################################################
    portfolioBalance = str(portfolioBalance)
    portfolioBalance = portfolioBalance.replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace(",", "").replace(
        "'", "")
    portfolioBalance=float(portfolioBalance)
    portfolioBalance=round(portfolioBalance,2)
    portfolioBalance=str(portfolioBalance)
    portfolioBalance='$ '+portfolioBalance

    ################################################
    #Average Return
    ################################################
    averageReturn = str(averageReturn)
    averageReturn = averageReturn.replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace(",",
                                                                                                                    "").replace(
        "'", "")
    averageReturn = float(averageReturn)
    averageReturn = round(averageReturn, 10)
    averageReturn = str(averageReturn)
    averageReturn = '% ' + averageReturn


    return render_template("index.html",portfolio=portfolio, portfolioBalance=portfolioBalance, averageReturn=averageReturn, fullQuery=everything)


if __name__ == "__main__":
    app.run(debug = True)

#set a special password path that runs the program. Only go to that path when you launch the app. Then it will run forever