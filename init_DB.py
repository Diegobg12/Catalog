from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, CatItem, User


engine = create_engine('postgresql://catalog:password@localhost/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()


Category1 = Category(name= "Soccer")
session.add(Category1)
session.commit()

Category2 = Category(name= "Basketball")
session.add(Category2)
session.commit()

Category3 = Category(name= "Baseball")
session.add(Category3)
session.commit()

Category4 = Category(name= "Frisbee")
session.add(Category4)
session.commit()

Category5 = Category(name= "Rock Climbing")
session.add(Category5)
session.commit()

Category6 = Category(name= "Foosball")
session.add(Category6)
session.commit()

Category7 = Category(name= "Skating")
session.add(Category7)
session.commit()

Category8 = Category(name= "Hockey")
session.add(Category8)
session.commit()

print("added categories items!")