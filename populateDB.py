from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Category, CatItem, Base

engine = create_engine('sqlite:///sportitmes.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Diego Bustos", email="diegobustos1229@gmail.com.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()


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

print "added categories items!"
