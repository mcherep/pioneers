from flask import Flask, request, render_template, jsonify
from models import *
from pony.orm import *
from collections import defaultdict

app = Flask(__name__)
app.config.from_envvar('SETTINGS', silent=True)

def expand_achievements(achievements):
    return map(lambda a: {"description": a.description,
                          "year": a.year,
                          "impact": a.impact.value,
                          "source": a.source}, achievements)

def expand_person(person, achievements):
    p = person.to_dict(only=["name", "country", "gender", "yob", "yod", "biography", "picture", "source"])
    p["achievements"] = expand_achievements(achievements)
    p["impact"] = reduce(lambda t, a: t + a["impact"], p["achievements"], 0)

    return p

def to_list(people):
    "Translates a dict of people->achievements into a list people."
    return [expand_person(p, a) for p, a in people.iteritems()]

def to_dict(people):
    "Collects a list of (person, achievement) into a dict of people->achievements."
    p = defaultdict(list)
    for k, v in people: p[k].append(v)

    return p

@app.route("/")
@db_session
def index():
    people = Person.select()
    return render_template("index.html", people=people)

@app.route("/people")
@db_session
def people():
    tags = request.args.getlist("tag")
    results = left_join((p, a) for p in Person
                               for a in p.achievements
                               for t in a.tags if t.name in tags)

    people = to_list(
               to_dict(results[:]))

    print people

    return jsonify(people=people)

if __name__ == "__main__":
    app.run()
