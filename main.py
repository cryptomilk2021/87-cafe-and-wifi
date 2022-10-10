from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


@app.route("/")
def home():
    cafes = db.session.query(Cafe).all()
    temp_dict = {}
    for cafe in cafes:
        temp_dict[cafe.id] = cafe.to_dict()

    return render_template("index.html", cafes=temp_dict)



@app.route("/random")
def random_cafe():
    cafes = db.session.query(Cafe).all()
    random_pick = random.choice(cafes)
    print(random_pick.name)

    return jsonify(random_pick.to_dict())
    # return random_pick.to_dict()

    # return jsonify(cafe={
    #     'id': random_pick.id,
    #     'name': random_pick.name,
    #     'map_url': random_pick.map_url,
    #     'img_url': random_pick.img_url,
    #     'location': random_pick.location,
    #     'amenities': {
    #         'seats': random_pick.seats,
    #         'has_toilet': random_pick.has_toilet,
    #         'has_wifi': random_pick.has_wifi,
    #         'has_sockets': random_pick.has_sockets,
    #         'can_take_calls': random_pick.can_take_calls,
    #         'coffee_price': random_pick.coffee_price}})

@app.route("/all")
def all_cafe():
    cafes = db.session.query(Cafe).all()
    temp_dict = {}
    for cafe in cafes:
        temp_dict[cafe.id] = cafe.to_dict()

    # random_pick = random.choice(cafes)
    # print(random_pick.name)
    #
    return jsonify(temp_dict)
    # return 'asdf'

@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})

@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})

@app.route("/update-price/", methods=["PATCH"])
def patch_new_price():
    cafe_id = request.args.get("cafe_id")
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(respons={"success": "Successfully update the price."}), 200
    else:
        return jsonify(respons={"Not found": "Sorry a cafe with that id was not found in the database."}), 404
    pass

@app.route("/report-closed/", methods=["DELETE"])
# def delete_cafe(cafe_id):
def delete_cafe():
    cafe_id = request.args.get("cafe_id")
    api_key = request.args.get("api_key")
    print(api_key)
    if api_key == "TopSecretAPIKey":
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

if __name__ == '__main__':
    app.run(debug=True)
