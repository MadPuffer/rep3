from data import db_session
from data.users import User
from data.news import News


db_session.global_init("db/blogs.sqlite")
session = db_session.create_session()
new = News(title='Title 4', description='somethin about 4', content='content 3')
user = session.query(User).first()
user.news.append(new)
session.commit()
