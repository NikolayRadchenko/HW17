# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}
db = SQLAlchemy(app)
api = Api(app)
movie_ns = api.namespace("movies")
director_ns = api.namespace("directors")
genre_ns = api.namespace("genres")


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Str()
    genre_id = fields.Int()
    genre = fields.Str()
    director_id = fields.Int()
    director = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movie_ns.route("/")
class MoviesView(Resource):
    def get(self):
        if request.args.get("director_id") and request.args.get("genre_id"):
            did = request.args.get("director_id")
            gid = request.args.get("genre_id")
            movies = db.session.query(Movie).filter(Movie.director_id == int(did)).filter(Movie.genre_id == int(gid))
            return movies_schema.dump(movies), 200
        elif request.args.get("director_id"):
            did = request.args.get("director_id")
            movies_director = db.session.query(Movie).filter(Movie.director_id == int(did))
            return movies_schema.dump(movies_director), 200
        elif request.args.get("genre_id"):
            gid = request.args.get("genre_id")
            movies_genre = db.session.query(Movie).filter(Movie.genre_id == int(gid))
            return movies_schema.dump(movies_genre), 200
        else:
            all_movies = db.session.query(Movie).all()
            return movies_schema.dump(all_movies), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        db.session.add(new_movie)
        db.session.commit()
        return "", 201


@movie_ns.route("/<int:mid>")
class MovieView(Resource):
    def get(self, mid):
        try:
            one_movie = db.session.query(Movie).get(mid)
            return movie_schema.dump(one_movie), 200
        except Exception as e:
            return e, 404

    def put(self, mid):
        movie = Movie.query.get(mid)
        if not movie:
            return "", 404
        req_json = request.json
        movie.title = req_json.get("title")
        movie.description = req_json.get("description")
        movie.trailer = req_json.get("trailer")
        movie.year = req_json.get("year")
        movie.rating = req_json.get("rating")
        movie.genre = req_json.get("genre")
        movie.director = req_json.get("director")
        db.session.add(movie)
        db.session.commit()
        return "", 204

    def delete(self, mid):
        movie = Movie.query.get(mid)
        if not movie:
            return "", 404
        db.session.delete(movie)
        db.session.commit()
        return "", 204


@director_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        all_directors = db.session.query(Director).all()
        return directors_schema.dump(all_directors), 200

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        db.session.add(new_director)
        db.session.commit()
        return "", 201


@director_ns.route("/<int:did>")
class DirectorView(Resource):
    def get(self, did: int):
        try:
            one_director = db.session.query(Director).get(did)
            return director_schema.dump(one_director), 200
        except Exception as e:
            return e, 404

    def put(self, did: int):
        director = Director.query.get(did)
        if not director:
            return "", 404
        req_json = request.json
        director.name = req_json.get("name")
        db.session.add(director)
        db.session.commit()
        return "", 204

    def delete(self, did: int):
        director = Director.query.get(did)
        if not director:
            return "", 404
        db.session.delete(director)
        db.session.commit()
        return "", 204


@genre_ns.route("/")
class GenresView(Resource):
    def get(self):
        all_genres = db.session.query(Genre).all()
        return genres_schema.dump(all_genres), 200

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        db.session.add(new_genre)
        db.session.commit()
        return "", 201


@genre_ns.route("/<int:gid>")
class GenreView(Resource):
    def get(self, gid: int):
        try:
            one_genre = db.session.query(Genre).get(gid)
            return genre_schema.dump(one_genre), 200
        except Exception as e:
            return e, 404

    def put(self, gid: int):
        genre = Genre.query.get(gid)
        if not genre:
            return "", 404
        req_json = request.json
        genre.name = req_json.get("name")
        db.session.add(genre)
        db.session.commit()
        return "", 204

    def delete(self, gid: int):
        genre = Genre.query.get(gid)
        if not genre:
            return "", 404
        db.session.delete(genre)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
