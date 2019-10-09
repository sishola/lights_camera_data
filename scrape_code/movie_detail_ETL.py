#!/usr/bin/env python
# coding: utf-8

# In[2]:


# Dependencies
import requests
import pymongo
import pandas as pd


# Extract tables containing movies with the highest grossing opening weekends from Box Office Mojo 

# In[3]:


# Box Office Mojo URL for films grossing $50M+
url = 'https://www.boxofficemojo.com/alltime/weekends/?pagenum=m50&sort=opengross&p=.htm&order=DESC'
# Box Office Mojo URL for films grossing $50-40M
url2 = 'https://www.boxofficemojo.com/alltime/weekends/?pagenum=m4050&sort=opengross&p=.htm&order=DESC'


# In[4]:


# Using pandas, find all tables on the url page
tables = pd.read_html(url)

# Since tables is a list of all the tables on the page, the required dataframe is stored in index 3
df = tables[3]
# Set the column names
df.columns = ['Rank', 'Title', 'Studio', 'Opening', '% of Total', 'Theaters', 'Average', 'Total Gross', 'Date']
# Remove first row since unnecessary row
df = df.iloc[1:]


# In[5]:


# Using pandas, find all tables on the url page
tables2 = pd.read_html(url2)

# Since tables is a list of all the tables on the page, the required dataframe is stored in index 3
df2 = tables2[3]
# Set the column names
df2.columns = ['Rank', 'Title', 'Studio', 'Opening', '% of Total', 'Theaters', 'Average', 'Total Gross', 'Date']
# Remove first row since unnecessary row
df2 = df2.iloc[1:]


# Transform the tables by:
# * merging them together and only pull the first 250 rows
# * replacing abbreviations with full names
# * changing column data types from objects to integers

# In[6]:


# Combine both dataframes into one using concat
boxOffice_df = pd.concat([df,df2])
# Extract only the top 250 highest grossing films
boxOffice_df = boxOffice_df.iloc[0:250]

#Replace abbreviated studio names with actual studio names
boxOffice_df['Studio'].replace(['BV', 'Uni.', 'WB', 'LGF' ,'Sony', 'Sum.' ,'LG/S', 'Fox' ,
                                'Par.', 'WB (NL)', 'P/DW' ,'DW', 'NM' ,'NL', 'MGM'], 
                               ['Buena Vista', 'Universal', 'Warner Bros.', 'Lionsgate' ,'Sony / Columbia', 
                                'Summit Entertainment' ,'Lionsgate' , '20th Century Fox' ,'Paramount', 'Warner Bros.',
                                'Paramount' ,'Dreamworks SKG', 'Newmarket' ,'New Line', 'MGM'], inplace=True)


# In[7]:


# Create a list of all the columns that need to be converted
string_to_int = ['Opening','Average','Total Gross']

# Initialize empty lists for new columns
opening = []
average = []
total_gross = []

# For each column that needs to be converted
for column in string_to_int:
    # For each row in the specified column
    for amount in boxOffice_df[column]:
        # Remove the $ symbol
        amount = amount[1:]
        # Remove all commas
        amount = amount.replace(',','')
        # Use if statetements to add the stripped amount to the correct list
        if column == 'Opening':
            opening.append(amount) 
        elif column == 'Average':
            average.append(amount)
        else:
            total_gross.append(amount)
    
# Update the columns with the integer amounts
boxOffice_df['Opening'] = pd.to_numeric(opening)
boxOffice_df['Average'] = pd.to_numeric(average)
boxOffice_df['Total Gross'] = pd.to_numeric(total_gross)
boxOffice_df["Rank"] = pd.to_numeric(boxOffice_df["Rank"])


# Extract additional film information from the OMBb API using the Title column in boxOffice_df.
# For films where there are discrepencies with the title format, imdb_ids are used to ensure correct data is pulled from the API.

# In[9]:


# Online Movie Database (OMDB) API URL including API Key and full plot
api_url = "http://www.omdbapi.com/?apikey=57e34fb6&plot=full"

movie_data = []
wrong_movies= {"MIB 3":'tt1409024',
           "Fast & Furious Presents: Hobbs & Shaw":'tt6806448',
           "Star Wars: The Force Awakens": 'tt2488496',
           "Marvel's The Avengers":'tt0848228',
           "The Divergent Series: Insurgent":'tt2908446',
           "Dr. Seuss' The Lorax":'tt1482459',
           "Monsters Vs. Aliens":'tt0892782',
           "Jackass 3-D":'tt1116184',
           "Dr. Seuss' The Grinch (2018)":'tt2709692',
           "Fantastic Four: Rise of the Silver Surfer":'tt0486576'}

# Using a for-loop...
for title in boxOffice_df['Title']:
    # If the title name is a key in wrong_movies, use the movie_id value when extracting from the API
    if title in wrong_movies:
        movie_id = wrong_movies[title]
        movie = requests.get(api_url + '&i=' + movie_id).json()
        # Only append to movie_data if Response is True (i.e. the film is in the API)
        if movie['Response'] == "True":
            movie_data.append(movie)
    # If the title includes brackets, usually for remakes e.g. Lion King (2019), first
    # extract the year and then remove all brackets from the title prior to running the API
    elif "(" in title:
        year = title[-5:][:-1]
        title = title[:-6]
        movie = requests.get(api_url + '&t=' + title + '&y=' + year).json()
        if movie['Response'] == "True":
            movie_data.append(movie)
    # Else, use the title to pull data from the API
    else:
        movie = requests.get(api_url + '&t=' + title).json()
        if movie['Response'] == "True":
            movie_data.append(movie)


# Data cleaning of the API includes:
# * inputing the list into a Pandas dataframe (movie_df)
# * creating a Rotten Tomatoes column
# * reformatting the Metascore column to ensure only numbers are present
# * transforming all ratings columns (IMDB, Metascore, Rotten Tomatoes) into float or integer data types
# * implementing a Rank column to match the one in boxOffice_df
# * seperating string elements in the Actors, Director, and Genre columns into lists of strings

# In[25]:


# Since the Rotten Tomatoes rating is found within the Ratings array, 
# extract it and append it to a seperate list
rotten_tomatoes = []

for movie in movie_data:
    try:
        rating = movie['Ratings'][1]['Value']
        if "/" in rating:
            rating = rating[0:2]
            rotten_tomatoes.append(rating)
        else:
            rating = rating[:-1]
            rotten_tomatoes.append(rating)
    except IndexError:
        rating = '0'
        rotten_tomatoes.append(rating)

# Since Metascore needs to be a number, all N/As are replaced with 0 and 
# fraction scores (e.g. 58/100) are split to only include the numerator   
metascore = []  

for movie in movie_data:
    score = movie['Metascore']
    if score == 'N/A':
        score = 0
        metascore.append(score)
    elif "/" in score:
        score = score[0:2]
        metascore.append(score)
    else:
        metascore.append(score)


# In[28]:


# Create a Pandas Dataframe
movie_df = pd.DataFrame(movie_data)
# Create a Rotten Tomatoes column
movie_df['Rotten Tomatoes'] = rotten_tomatoes
# Update the Metascore column
movie_df['Metascore'] = metascore
# Create a Rank column using the index
movie_df = movie_df.reset_index()
movie_df['Rank'] = movie_df['index'] + 1

# Select only the necessary columns
df = movie_df[['Rank','Title','Plot','Actors', 'Director', 'Genre', 'Poster', 
               'Rated', 'imdbRating', 'Metascore','Rotten Tomatoes']]


# In[33]:


# Since certain columns have strings of words or names, transform those columns so that 
# they contain a list of strings instead
split_columns = ['Actors','Director','Genre']

split_actors = []
split_directors = []
split_genre = []

# For Actors, Director, and Genre, seperate the string using ", "
for column in split_columns:
    for row in df[column]:
        split_row = row.split(", ")
        if column == 'Actors':
            split_actors.append(split_row)
        elif column == 'Director':
            split_directors.append(split_row)
        else:
            split_genre.append(split_row)

# For data cleanliness, copy the df to a new dataframe and update the necessary columns
split_df = df.copy()
split_df['Actors'] = split_actors
split_df['Director'] = split_directors
split_df['Genre'] = split_genre

# Transform all rating related columns into numeric data types (either integer or float)
split_df['imdbRating'] = pd.to_numeric(split_df['imdbRating'])
split_df['Metascore'] = pd.to_numeric(split_df['Metascore'])
split_df['Rotten Tomatoes'] = pd.to_numeric(split_df['Rotten Tomatoes'])


# In[34]:


# Since titles are slightly different, merge both dataframes based on Rank
final_df = boxOffice_df.merge(split_df,left_on = 'Rank',right_on='Rank')
# Select all necessary columns
final_df = final_df[['Rank', 'Title_x', 'Studio', 'Opening', '% of Total', 'Theaters',
       'Average', 'Total Gross', 'Date', 'Plot', 'Actors',
       'Director', 'Genre', 'Poster', 'Rated', 'imdbRating', 'Metascore','Rotten Tomatoes']]
# Rename Title column for clarity
final_df = final_df.rename(columns={"Title_x": "Title"})


# In[16]:


# Create list of dictionaries in order to efficiently insert into MongoDB
movies_dict = new_df.to_dict('records')


# Create a MongoDB connection and insert the complete movies_dict into the movie_detail collection

# In[17]:


# MongoDB connection
conn = 'mongodb+srv://generaluser:generaluser123@project2-ha8my.mongodb.net/movie_db?retryWrites=true&w=majority'
client = pymongo.MongoClient(conn)

# Declare the collection
collection = client.movie_db.movie_detail
#Drop collection if it exists to prevent duplication
collection.drop()  
# Insert all of the documents into the collection
collection.insert_many(movies_dict)

