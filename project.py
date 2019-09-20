
from flask import Flask, render_template, request, redirect, url_for, jsonify
app = Flask(__name__)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, CatItem, User
# Init DATABASE
engine = create_engine('sqlite:///sportitmes.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Funtions for user log in-----------------------------------------





# Json for CATALOG--------------------------------------------------
@app.route('/Catalog/JSON')
def catalogJSON():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Items = session.query(CatItem).all()
    return jsonify(CatItem=[i.serialize for i in Items])


# CRUD FUNCTIONS ---------------------------------------------------
@app.route('/')
@app.route('/catalog')
def showCategories():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Categories = session.query(Category).all()
    Items = session.query(CatItem).all()
    return render_template('home.html', Categories = Categories, Items = Items)

@app.route('/catalog/<cat_name>')
@app.route('/catalog/<cat_name>/items')
def showItems(cat_name):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Categories = session.query(Category).all()
    Cat = session.query(Category).filter_by(name = cat_name).one()
    Items = session.query(CatItem).filter_by(cat_name = Cat.name)
    return render_template('items.html', Categories = Categories, Items = Items, Cat = Cat)


@app.route('/catalog/<cat_name>/<item_name>')
@app.route('/catalog/<cat_name>/<item_name>/<item_id>')
def ItemDescription(cat_name, item_name, item_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Cat = session.query(Category).filter_by(name = cat_name).one()
    Item = session.query(CatItem).filter_by(id = item_id).one()
    return render_template('description.html', Cat = Cat, Item = Item, cat_name = cat_name)


@app.route('/catalog/<cat_name>/new', methods=['GET', 'POST'])
def createItem(cat_name):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if request.method == 'POST':
        Items = session.query(Category).filter_by(name = cat_name)
        newItem = CatItem(
        name = request.form['name'],
        description = request.form['Description'],
        cat_name = cat_name)
        session.add(newItem)
        session.commit()
        return redirect(url_for('showItems', cat_name = cat_name))
    else:
        return render_template('createItem.html', cat_name = cat_name)


@app.route('/catalog/<cat_name>/<item_name>/<item_id>/edit', methods=['GET', 'POST'])
def editItems(cat_name, item_name, item_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    editedItem = session.query(CatItem).filter_by(id = item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['Description']:
            editedItem.description = request.form['Description']
        if request.form['Category']:
            editedItem.cat_name = request.form['Category']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('showItems', cat_name = cat_name))
    else:
        return render_template(
            'editItem.html', cat_name=cat_name, item_name = item_name, item_id = item_id )

@app.route('/catalog/<cat_name>/<item_name>/<item_id>/delete', methods=['GET', 'POST'])
def deleteItem(cat_name, item_name, item_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    itemToDelete = session.query(CatItem).filter_by(id = item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showItems', cat_name = cat_name))
    else:
        return render_template('deleteItem.html', cat_name = cat_name, itemToDelete = itemToDelete)



if __name__ == '__main__':
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)
