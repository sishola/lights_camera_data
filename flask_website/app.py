from flask import Flask, render_template, jsonify
import pymongo
from flask_pymongo import PyMongo

app = Flask(__name__)

# setup mongo connection
mongo = PyMongo(
    app, uri="mongodb+srv://generaluser:generaluser123@project2-ha8my.mongodb.net/movie_db?retryWrites=true&w=majority")

@app.route('/')
def index():
    # write a statement that finds all the items in the db and sets it to a variable
    movies = list(mongo.db.movie_detail.find())

    # render an index.html template and pass it the data you retrieved from the database
    return render_template("index.html", movies=movies)


@app.route('/json')
def jsonified():
    docs = []
    for doc in mongo.db.movie_detail.find():
        # removes the _id element
        doc.pop('_id')
        # appends each document into the list
        docs.append(doc)
    # returns a json page    
    return jsonify(docs)


@app.route('/movie_ring')
def movie_ring():
    return render_template("movie_ring.html")

@app.route('/bubble')
def bubble():
    return render_template("bubble.html")


@app.route('/word_cloud')
def word_cloud():
    return render_template("word_cloud.html")


@app.route('/sankey')
def sankey():
    return render_template("sankey.html")


@app.route('/treemap')
def treemap():
    return render_template("treemap.html")


@app.route("/map")
def init():
    return render_template("map.html")


@app.route("/filterLessRange_IG_Rank/<value>")
def filterRankRange(value):
    # return items from a different collection (international_gross_det) base on the rank
    value = int(value)
    docs = []
    # select data less or equal the rank selected
    for doc in mongo.db.international_gross_det.find({'rank': {'$lte': value}}):
        doc.pop('_id')
        docs.append(doc)
    return jsonify(docs)


@app.route("/filterLessEq_IG_Rank/<value>")
def filterRank(value):
    # return items from a different collection (international_gross_det) base on the rank
    value = int(value)
    docs = []
    # select data equal the rank selected
    for doc in mongo.db.international_gross_det.find({'rank': value}):
        doc.pop('_id')
        docs.append(doc)
    return jsonify(docs)


if __name__ == "__main__":
    app.run(debug=True)
