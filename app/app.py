from flask import Flask, render_template
from flask_pymongo import PyMongo
import scrape_mars

app = Flask(__name__)


mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")


@app.route("/")
def index():
    mars = mongo.db.mars.find_one()
    return render_template("index.html", mars=mars)


@app.route("/scrape")
def scrape():
    mars = mongo.db.mars
    mars_data = scrape_mars.scrape()
    mars.update({}, mars_data, upsert=True)
    print("Scraping Successful!")
    # Adding template so that the data is updated in UI with a button for navigating back to homepage
    mars = mongo.db.mars.find_one()
    return render_template("scrape.html", mars=mars)
    


if __name__ == "__main__":
    app.run()
