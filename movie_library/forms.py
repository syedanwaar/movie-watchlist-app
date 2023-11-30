from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, TextAreaField, URLField, PasswordField
from wtforms.validators import NumberRange, InputRequired, Email, Length, EqualTo

class MovieForm(FlaskForm):
    title=StringField("Title", validators=[InputRequired()])
    director=StringField("Director", validators=[InputRequired()])

    year=IntegerField("Year", validators=[InputRequired(), NumberRange(min=1878,message="Enter year in yyyy format")])

    submit=SubmitField("Add Movie")

class StringListField(TextAreaField):
    def _value(self):
        if self.data:
            return "\n".join(self.data)
        else:
            return ""
    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            self.data=[line.strip() for line in valuelist[0].split('\n')]
        else:
            self.data=[]


class ExtendedMovieForm(MovieForm):
    cast = StringListField("Cast")
    series=StringListField('Series')
    tags=StringListField("Tags")
    description= StringField("Description")
    video_link=URLField("Video link")

    submit=SubmitField("Submit")

class RegisterForm(FlaskForm):
    email=StringField("Email", validators=[InputRequired(), Email()])
    password=PasswordField("Password", validators=[InputRequired(), Length(min=4, message="Your password must contain atleast 4 character.")])
    confirm_password=PasswordField("Confirm password", validators=[InputRequired(), EqualTo("password", message="Password dosen't match.")])
    submit=SubmitField("Reegister")

class LoginForm(FlaskForm):
    email=StringField("Email", validators=[InputRequired(), Email()])
    password=PasswordField("Password", validators=[InputRequired()])
    submit=SubmitField("Login")