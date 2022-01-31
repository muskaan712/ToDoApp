from flask import Flask, render_template, flash
from flask.helpers import url_for
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from pymongo import MongoClient
from command_functions import addTodoItem, editTodoItem, searchItem, deleteTodoItem
import os

MY_SECRET_KEY = os.urandom(32)

# Mongo Setup
# Create a new database with name "cliTodoListDatabase" in Mongo DB Atlas and access it like bellow
client = MongoClient("mongodb+srv://muskaan:mukkukuhu@cluster0.xwwad.mongodb.net/flaskapi?retryWrites=true&w=majority")

db = client.get_database("cliTodoListDatabase") 

db_todos_collection = db.get_collection("Todos")
# Setup index for search for todo_name
db_todos_collection.create_index([('todo_name', 'text')])

app = Flask(__name__)

app.config['SECRET_KEY'] = MY_SECRET_KEY

class TodoForm(FlaskForm):
    todo_input = StringField(label="User entry:", validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField(label="Submit")

class UpdateForm(FlaskForm):
    id_input = StringField(label="Todo's ID:", validators=[DataRequired(), Length(min=1, max=100)])
    new_text_input = StringField(label="New text", validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField(label="Submit")

@app.route("/", methods=["GET", "POST"])
def home():
    cursor = list(db_todos_collection.find({}))
    return render_template("home.html", cursor=cursor)

@app.route("/create", methods=["GET", "POST"])
def create():
    form = TodoForm()
    form.todo_input.render_kw = {"placeholder": "Create a new TODO"}
    todo_input = form.todo_input.data
    if form.validate_on_submit():
        flash("Item successfully added.", "success")
        addTodoItem(db_todos_collection, todo_input)
        return redirect(url_for("home"))
    return render_template("create.html", form=form, title="create")

@app.route("/read", methods=["GET", "POST"])
def read():
    form = TodoForm()
    form.todo_input.render_kw = {"placeholder": "Type i.e. 'clean'"}
    todo_input = form.todo_input.data
    if form.validate_on_submit():
        cursor = searchItem(db_todos_collection, todo_input)
        if cursor:
            flash("Item(s) successfully found.", "success")
            return render_template("read.html", form=form, cursor=cursor)
        else:
            flash("Item(s) not found.", "fail")
            return render_template("read.html", form=form, cursor=cursor)

    return render_template("read.html", form=form, title="read")

@app.route("/update", methods=["GET", "POST"])
def update():
    form = UpdateForm()
    form.id_input.render_kw = {"placeholder": "Enter todo's ID"}
    form.new_text_input.render_kw = {"placeholder": "Enter todo's new text"}
    id_input = form.id_input.data
    new_text_input = form.new_text_input.data
    if form.validate_on_submit():
        exists = editTodoItem(db_todos_collection, id_input, new_text_input)
        if exists:
            flash("Item successfully updated.", "success")
            return redirect(url_for("home"))
        else:
            flash("Item not found.", "fail")
            return redirect(url_for("update"))

    return render_template("update.html", form=form, title="update")

@app.route("/delete", methods=["GET", "POST"])
def delete():
    form = TodoForm()
    form.todo_input.render_kw = {"placeholder": "Delete by ID"}
    todo_input = form.todo_input.data
    if form.validate_on_submit():
        exists = deleteTodoItem(db_todos_collection, todo_input)
        if exists:
            flash("Item successfully deleted.", "success")
            return redirect(url_for("home"))
        else:
            flash("Item not found.", "fail")
            return redirect(url_for("delete"))

    return render_template("delete.html", form=form, title="delete")

if __name__ == "__main__":
    app.run()