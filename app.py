from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import os
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Hostel, Review

app = Flask(__name__)

# Database configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'hostels.db')
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'hostel-review-secret-key-change-in-prod')
app.config['SESSION_TYPE'] = 'filesystem'

db.init_app(app)
Session(app)

# Ensure upload directory exists
UPLOADS_DIR = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOADS_DIR, exist_ok=True)


@app.before_request
def create_tables():
    """Create database tables on first request."""
    db.create_all()


def save_hostel_image(file_storage):
    if not file_storage:
        return ''
    filename = secure_filename(file_storage.filename)
    if filename == '':
        return ''
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    path = os.path.join(UPLOADS_DIR, unique_name)
    file_storage.save(path)
    return f"/static/uploads/{unique_name}"


def average_rating_for(hostel_id):
    reviews = Review.query.filter_by(hostel_id=hostel_id).all()
    reviews_with_rating = [r for r in reviews if r.rating_overall is not None]
    if not reviews_with_rating:
        return None
    avg = sum(r.rating_overall for r in reviews_with_rating) / len(reviews_with_rating)
    return round(avg, 2)


def average_ratings_for(hostel_id):
    reviews = Review.query.filter_by(hostel_id=hostel_id).all()
    if not reviews:
        return {
            'overall': None, 'food': None, 'cleaning': None, 
            'staff': None, 'location': None, 'owner': None
        }
    
    def avg(attr_name):
        vals = [getattr(r, attr_name) for r in reviews if getattr(r, attr_name) is not None]
        return round(sum(vals) / len(vals), 2) if vals else None
    
    return {
        'overall': avg('rating_overall'),
        'food': avg('rating_food'),
        'cleaning': avg('rating_cleaning'),
        'staff': avg('rating_staff'),
        'location': avg('rating_location'),
        'owner': avg('rating_owner')
    }



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            return redirect(url_for('hostels'))
        else:
            return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        name = request.form.get('name', '').strip()
        
        if not email or not password or not name:
            return render_template('signup.html', error='All fields required')
        if password != confirm_password:
            return render_template('signup.html', error='Passwords do not match')
        if len(password) < 4:
            return render_template('signup.html', error='Password must be at least 4 characters')
        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error='Email already registered')
        
        new_user = User(
            email=email,
            password_hash=generate_password_hash(password),
            name=name
        )
        db.session.add(new_user)
        db.session.commit()
        
        session['user_id'] = new_user.id
        session['user_name'] = new_user.name
        session['user_email'] = new_user.email
        return redirect(url_for('hostels'))
    return render_template('signup.html')



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/hostels')
def hostels():
    q = request.args.get('q', '').strip().lower()
    hostels_list = Hostel.query.all()
    
    if q:
        hostels_list = [h for h in hostels_list if q in (h.name or '').lower() or q in (h.location or '').lower()]
    
    # Attach ratings and reviews
    for h in hostels_list:
        h.avg_rating = average_rating_for(h.id)
        h.reviews = Review.query.filter_by(hostel_id=h.id).all()
        av = average_ratings_for(h.id)
        h.rating_counts = {
            'overall': av['overall'],
            'food': av['food'],
            'cleaning': av['cleaning'],
            'staff': av['staff'],
            'location': av['location'],
            'owner': av['owner']
        }
    
    return render_template('hostels.html', hostels=hostels_list, query=request.args.get('q', ''), current_user=session.get('user_id'))


@app.route('/review')
def review_form():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    hostels_list = Hostel.query.all()
    selected = request.args.get('hostel_id')
    return render_template('review.html', hostels=hostels_list, selected=selected)


@app.route('/submit_review', methods=['POST'])
def submit_review():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    hostel_id = request.form.get('hostel_id')
    new_hostel_name = request.form.get('new_hostel_name', '').strip()
    new_hostel_location = request.form.get('new_hostel_location', '').strip()
    
    # Collect category ratings
    rating_overall = request.form.get('rating_overall')
    rating_food = request.form.get('rating_food')
    rating_cleaning = request.form.get('rating_cleaning')
    rating_staff = request.form.get('rating_staff')
    rating_location = request.form.get('rating_location')
    rating_owner = request.form.get('rating_owner')
    comment = request.form.get('comment', '').strip()
    
    def to_float(v):
        try:
            return float(v) if v is not None and str(v).strip() != '' else None
        except Exception:
            return None
    
    if new_hostel_name:
        # Create new hostel with optional image
        file = request.files.get('new_hostel_image')
        image_path = save_hostel_image(file)
        new_hostel = Hostel(
            name=new_hostel_name,
            location=new_hostel_location,
            description='',
            image=image_path
        )
        db.session.add(new_hostel)
        db.session.commit()
        hostel_id = new_hostel.id
    
    if hostel_id:
        new_review = Review(
            hostel_id=hostel_id,
            reviewer_id=session.get('user_id'),
            reviewer_name=session.get('user_name', 'Anonymous'),
            rating_overall=to_float(rating_overall),
            rating_food=to_float(rating_food),
            rating_cleaning=to_float(rating_cleaning),
            rating_staff=to_float(rating_staff),
            rating_location=to_float(rating_location),
            rating_owner=to_float(rating_owner),
            comment=comment
        )
        db.session.add(new_review)
        db.session.commit()
    
    return redirect(url_for('hostels'))



def rating_counts_for(hostel_id):
    reviews = Review.query.filter_by(hostel_id=hostel_id).all()
    counts = {str(i): 0 for i in range(1, 6)}
    for r in reviews:
        if r.rating_overall is not None:
            key = str(int(r.rating_overall))
            if key in counts:
                counts[key] += 1
    return counts


@app.route('/export_reviews')
def export_reviews():
    hostel_id = request.args.get('hostel_id')
    if hostel_id:
        reviews_list = Review.query.filter_by(hostel_id=hostel_id).all()
    else:
        reviews_list = Review.query.all()
    
    # Build CSV with all rating categories
    csv_lines = ['hostel_id,reviewer_id,reviewer_name,rating_overall,rating_food,rating_cleaning,rating_staff,rating_location,rating_owner,comment,date']
    for r in reviews_list:
        row = [
            r.hostel_id or '',
            r.reviewer_id or '',
            (r.reviewer_name or '').replace('"', '""'),
            str(r.rating_overall or ''),
            str(r.rating_food or ''),
            str(r.rating_cleaning or ''),
            str(r.rating_staff or ''),
            str(r.rating_location or ''),
            str(r.rating_owner or ''),
            (r.comment or '').replace('"', '""'),
            r.created_at.isoformat() if r.created_at else ''
        ]
        csv_lines.append('"' + '","'.join(row) + '"')
    
    csv_text = '\n'.join(csv_lines)
    return Response(csv_text, mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=reviews.csv"})


@app.route('/api/hostels')
def api_hostels():
    hostels_list = Hostel.query.all()
    return jsonify([{
        'id': h.id,
        'name': h.name,
        'location': h.location,
        'description': h.description,
        'image': h.image
    } for h in hostels_list])


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
