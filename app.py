from flask import Flask,render_template,url_for,request
from flask_bootstrap import Bootstrap
import pandas as pd
import numpy as np
import warnings

import smtplib

warnings.filterwarnings("ignore")


app = Flask(__name__)
Bootstrap(app)
@app.route('/')
def index():
    movies_titles = pd.read_csv("data/Movie_Id_Titles")
    movies_list = movies_titles['title'].values.tolist()
    return render_template('index.html',movies = movies_list)

@app.route('/predict', methods=['POST'])
def predict():
    column_names = ['user_id','item_id','rating','timestamp']
    df = pd.read_csv("data/u.data",sep="\t",names=column_names)
    movie_titles = pd.read_csv("data/Movie_Id_Titles")
    df = pd.merge(df,movie_titles,on='item_id')

    ratings = pd.DataFrame(df.groupby('title')['rating'].mean())
    ratings['num_of_ratings'] = pd.DataFrame(df.groupby('title')['rating'].count())
    moviemat = df.pivot_table(values='rating',index='user_id',columns='title')

    argument = request.form['choice']
    user_name = request.form['username']
    starwars_ratings = moviemat[argument]
    starwars_ratings.dropna(inplace=True)
    corr_starwars = moviemat.corrwith(starwars_ratings)
    like_starwars = pd.DataFrame(corr_starwars,columns=['Correlation'])
    like_starwars.dropna(inplace=True)
    like_starwars = like_starwars.join(ratings['num_of_ratings'])
    like_starwars = like_starwars.join(ratings['rating'])
    result = like_starwars[like_starwars['num_of_ratings']>100].sort_values('Correlation',ascending=False)
    res=result.index[1:11]
    res_df = pd.DataFrame(data=res)
    recommendations = res_df['title'].values.tolist()
    movie_rating = result['rating'].values.tolist()

    from_email = 'quadeershaikh15.8@gmail.com'
    password = '9619wr10@'
    send_to_email = request.form['e_mail']
    message = '\n'.join(recommendations)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)
    server.sendmail(from_email, send_to_email , message)
    server.quit()



    return render_template('result.html',prediction = recommendations,username = user_name)

if __name__ == '__main__':
	app.run(debug=True)
