from app import app, db
from models import Hostel, Review, User

with app.app_context():
    hostels = Hostel.query.all()
    print('Hostel count:', len(hostels))
    for h in hostels:
        print(h.id, '|', h.name, '|', h.location, '| reviews=', len(h.reviews))
    reviews = Review.query.all()
    print('Review count:', len(reviews))
    users = User.query.all()
    print('User count:', len(users))
