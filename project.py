
from flask import Flask, render_template, request, redirect, url_for, jsonify
app = Flask(__name__)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, CatItem

engine = create_engine('sqlite:///sportitmes.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/catalog')
def showCategories():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Categories = session.query(Category).all()
    return render_template('home.html', Categories = Categories)

@app.route('/catalog/<cat_name>')
@app.route('/catalog/<cat_name>/items')
def showItems(cat_name):
    # return "This Page will show all categories and the last item added"
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Categories = session.query(Category).all()
    Cat = session.query(Category).filter_by(name = cat_name).one()
    Items = session.query(CatItem).filter_by(cat_name = Cat.name)
    return render_template('items.html', Categories = Categories, Items = Items, Cat = Cat)

@app.route('/catalog/<cat_name>/<item_name>')
def ItemDescription(cat_name, item_name):
    # return "This Page will show all categories and the last item added"
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Cat = session.query(Category).filter_by(name = cat_name).one()
    Item = session.query(CatItem).filter_by(name = item_name, cat_name = cat_name).one()
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


@app.route('/catalog/<catname>/<item>/edit', methods=['GET', 'POST'])
def editItems(cat_name, item_name):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    editedItem = session.query(CatItem).filter_by(cat_name = catname).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['Description']:
            editedItem.description = request.form['Description']
        if request.form['Category']:
            editedItem.description = request.form['Category']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('showItems', cat_name = catname))
    else:
        return render_template(
            'editItem.html', cat_name=catname, item=editedItem)

# @app.route('/catalog/<catalog>/<item>/delete', methods=['GET', 'POST'])
# def deleteItem(restaurant_id,menu_id):
#     DBSession = sessionmaker(bind=engine)
#     session = DBSession()
#     itemToDelete = session.query(CatItem).filter_by(name=item_name).one()
#     if request.method == 'POST':
#         session.delete(itemToDelete)
#         session.commit()
#         return redirect(url_for('showMenu', restaurant_id=restaurant_id))
#     else:
#         return render_template('deleteMenu.html', cat_name=catname, item_name = item_name)



if __name__ == '__main__':
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)
