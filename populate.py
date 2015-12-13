from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup_list import Base, Subjects, Response, User

engine = create_engine('sqlite:///subjecsandrespnse.db')
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
User1 = User(name="Liliana Vess", email="lili@magic.com",
             picture='http://magic.wizards.com/sites/mtg/files/images/hero/Liliana_Vess_640.jpg')
session.add(User1)
session.commit()

User2 = User(name="Gideon", email="giddy@magic.com",
             picture='http://www.artofmtg.com/wp-content/uploads/2015/07/Gideon-Battle-Forged-Magic-Origins-Art.jpg')
session.add(User2)
session.commit()

# Menu for UrbanBurger
subject1 = Subjects(user_id=1, title="Manaless Magic", body="Have you ever tried magic without mana?")

session.add(subject1)
session.commit()

response1 = Response(user_id=2, text = "How can you cast spells without magic?", subjects = subject1)

session.add(response1)
session.commit()

response2 = Response(user_id=1, text = "You cast from the graveyard!", subjects = subject1)

session.add(response2)
session.commit()

subject2 = Subjects(user_id=2, title="Zombie Defense", body="Walls that will never crumble keep out the undead")

session.add(subject2)
session.commit()

response3 = Response(user_id=1, text = "Even 1... BILLION zombies?", subjects = subject2)

session.add(response3)
session.commit()

response4 = Response(user_id=2, text = "Yes.", subjects = subject2)

session.add(response4)
session.commit()

print "added menu items!"
