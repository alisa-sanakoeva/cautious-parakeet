# ეს არის ამ დავალების შესრულების პროცესში ჩემი ყურადღების გაფანტვის მიზეზების database
# ანუ რეალურად ყოველ ჯერზე უბრალოდ ყურადღება კი არ მეფანტებოდა,
# არამედ მონაცემებს ვაგროვებდი ამ დავალებისთვის.

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Resource, Api, reqparse

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

Migrate(app, db)

api = Api(app)


class Distractions(db.Model):
    __tablename__ = "Distractions"

    id = db.Column(db.Integer, primary_key=True)
    distraction = db.Column(db.String)
    time_lost = db.Column(db.Integer)  # minutes

    def __init__(self, distraction, time_lost):
        self.distraction = distraction
        self.time_lost = time_lost

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def json(self):
        return {'id': self.id, 'distraction': self.distraction, 'time_lost': self.time_lost}


class GetPost(Resource):
    def get(self):
        data = Distractions.query.filter_by().all()
        distractions = []
        for d in data:
            distractions.append(d.json())
        return {"message": distractions}

    def post(self):

        data = IdResource.parser.parse_args()
        dist = Distractions(data['distraction'], data['time_lost'])
        try:
            dist.create()
        except Exception as e:
            return {"message": f'{e}'}
        else:
            return f'New distraction unlocked: {dist.json()}', 200



class IdResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('distraction',
                        type=str,
                        required=True,
                        help="Did you get distracted while writing a distraction?"
                        )

    parser.add_argument('time_lost',
                        type=int,
                        required=True,
                        help="How much time did you waste?"
                        )

    def get(self, id):
        dist = Distractions.find_by_id(id)
        if dist:
            return dist.json()
        else:
            return {"message": f'id {id} is nonexistent yet, perhaps you got distracted while adding it'}, 404


    def put(self, id):
        dist = Distractions.find_by_id(id)
        data = IdResource.parser.parse_args()

        if dist:
            dist.distraction = data["distraction"]
            dist.time_lost = data["time_lost"]
        else:
            dist = Distractions(data["distraction"], data["time_lost"])

        dist.create()

        return {"message": f"შენახულია მონაცემი {dist.json()}"}

    def delete(self, id):
        dist = Distractions.find_by_id(id)

        if dist:
            dist.delete_from_db()
            return {"message": f"მონაცემი {id} წაშლილია"}
        else:
            return {"message": f"ბაზაში არც არასდროს ყოფილა {id} ელემენტი"}



data = [("სნექების აღება", 5),
        ("იმის გახსენება თუ სად არის წინა კურსის დოკუმენტაციები", 5),
        ("ძველი დავალებების ნახვა და ნოსტალგირება", 30),
        ("ჩემი დისთვის rickrolling-ის ახსნა", 7),
        ("Google: რატომ აქვს ტუკანს ამხელა ნისკარტი", 2),
        ("ხელზე სამაჯურის მიბმა რომელიც შემახსენებს რომ საქმეს უნდა დავუბრუნდე", 2),
        ("ვიდეოს ყურება პროკრასტინაციის შეწყვეტის მეთოდებზე", 10),
        ("ჩაის დასხმა", 3),
        ("IQ ტესტის გავლა", 10),
        ("ყავის დასხმა კონცენტრაციისთვის", 3),
        ("Google: ჰქონდა თუ არა აინშტაინს აუტიზმის სინდრომი", 2),
        ("პანიკა იმაზე რომ პოსტმენი როგორ მუშაობს არ მახსოვს და დრო მეწურება", 2)
        ]


db.init_app(app)
db.create_all()
if not Distractions.query.first():
    for item in data:
        dist = Distractions(item[0], item[1])
        db.session.add(dist)
    db.session.commit()

api.add_resource(IdResource, '/distractions/<int:id>')
api.add_resource(GetPost, '/distractions')

app.run(port=5000, debug=True)
