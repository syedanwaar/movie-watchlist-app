from flask import Blueprint, render_template, session, redirect, url_for, request, current_app, flash
from movie_library.forms import MovieForm, ExtendedMovieForm, RegisterForm, LoginForm
from movie_library.models import Movie, User
from dataclasses import asdict
import datetime
import uuid
from passlib.hash import pbkdf2_sha256
from functools import wraps

pages=Blueprint("pages", __name__, template_folder="templates", static_folder="static")


def login_required(route):
    @wraps(route)
    def route_wrapper(*args,**kwargs):
        if session.get('email') == None:
            return redirect(url_for('pages.login'))
        
        return route(*args,**kwargs)
    
    return route_wrapper


@pages.route("/")
@login_required
def index():
    movies_data=current_app.db.movie.find({'user_id':session.get('user_id')})
    movies=[Movie(**movie) for movie in movies_data]
    return render_template("index.html", title='Movies Watchlist', movies_data=movies)

@pages.route("/register", methods=["POST","GET"])
def register():
    if session.get('email'):
        return redirect(url_for("pages.index"))
    form = RegisterForm()
    
    if form.validate_on_submit():
        user= User(
            _id=uuid.uuid4().hex,
            email=form.email.data,
            password=pbkdf2_sha256.hash(form.password.data)
        )
        current_app.db.user.insert_one(asdict(user))

        flash("User registered Successfully", "success")

        return redirect(url_for("pages.login"))
    
    return render_template("register.html", title="Movies Watchlist - Register", form=form)

@pages.route('/login', methods=['POST',"GET"])
def login():
    if session.get('email'):
        return redirect(url_for('pages.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user_data=current_app.db.user.find_one({"email":form.email.data})
        if not user_data:
            flash("Incorrect login credentials", category="danger")
            return redirect(url_for("pages.login"))
        user=User(**user_data)

        if user and pbkdf2_sha256.verify(form.password.data, user.password):
            session['user_id']=user._id
            session['email']=user.email

            return redirect(url_for('pages.index'))
        
        flash("Incorrect login credentials.", category="danger")
    
    return render_template('login.html', title='Movies Watchlist - Login', form=form)

@pages.route('/movie/<string:_id>')
@login_required
def movie(_id:str):
    movie_data=current_app.db.movie.find_one({'_id':_id, 'user_id':session.get('user_id')})
    movie=Movie(**movie_data)

    return render_template('movie_details.html',movie=movie)

@pages.route('/movie/<string:_id>/rate')
@login_required
def rate_movie(_id):
    rating=int(request.args.get('rating'))
    current_app.db.movie.update_one({'_id':_id}, {'$set':{'rating':rating}})
    return redirect(url_for("pages.movie",_id=_id))

@pages.route('/movie/<string:_id>/watch')
def watch_today(_id):
    current_app.db.movie.update_one({'_id':_id}, {'$set':{'last_watched':datetime.datetime.today()}})
    return redirect(url_for("pages.movie",_id=_id))

@pages.route("/add" ,methods=['GET','POST'])
@login_required
def add_movie():
    form=MovieForm()
    
    if form.validate_on_submit():
        movie=Movie(_id=uuid.uuid4().hex,
            title=form.title.data,
            director=form.director.data,
            year=form.year.data,
            user_id=session.get('user_id')
        )
        current_app.db.movie.insert_one(asdict(movie))
        return redirect(url_for("pages.index"))

    return render_template('new_movie.html',title="Movies Watchlist - Add Movie", form=form)

@pages.route("/edit/<string:_id>", methods=["POST","GET"])
@login_required
def edit_movie(_id):
    movie=Movie(**current_app.db.movie.find_one({"_id":_id}))
    form= ExtendedMovieForm(obj=movie)

    if form.validate_on_submit():
        movie.title=form.title.data
        movie.director=form.director.data
        movie.year=form.year.data
        movie.cast=form.cast.data
        movie.tags=form.tags.data
        movie.series=form.series.data
        movie.description=form.description.data
        movie.video_link=form.video_link.data

        current_app.db.movie.update_one({"_id":_id},{"$set":asdict(movie)})

        return redirect(url_for("pages.movie",_id=_id))
    else:
        return render_template("movie_form.html", movie=movie, form=form) 

@pages.route("/delete/movie/<string:_id>")
def delete_movie(_id):
    current_app.db.movie.delete_one({'_id':_id,'user_id':session.get('user_id')})
    return redirect(url_for('pages.index'))

@pages.route("/logout")
def logout():
    current_theme=session.get('theme')
    session.clear()
    session['theme']=current_theme
    return redirect(url_for('pages.login'))

@pages.route("/toggle-theme")
def toggle_theme():
    current_theme=session.get("theme")
    if current_theme=='dark':
        session['theme']='light'
    else:
        session['theme']='dark'
    return redirect(request.args.get("current_page"))

