from flask_pymongo import PyMongo


def init_db():
    mongo = PyMongo()
    return mongo


def get_db(app, mongo):
    app.config["MONGO_URI"] = "mongodb+srv://main:fYOpqtsmGKmSMtcc@cluster0.lkdcc.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
    mongo.init_app(app)