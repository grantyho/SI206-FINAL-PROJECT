import unittest
import sqlite3
import os
import plotly.graph_objects as go
import statistics


# Connects to database to pull data from tables in database 
# Has db_name as a parameter, a string, for the database file name
# returns cur and conn 
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

# Compiles data from the 'Calculation_Table' into a dictionary which is returned:
    # {'Fake News': #, 'True News': #}
# Takes curr + conn (for connecting to database)
def mlClassificationData(cur, conn):
    cur.execute('SELECT ml_classification FROM Calculation_Table')
    ml_classification_list = list(cur.fetchall())
    ml_pie = {}

    fake_count = 0
    true_count = 0

    for i in ml_classification_list:

        classification = i[0]

        if classification == 0:
            fake_count += 1 
            ml_pie['Fake News'] = fake_count

        else: 
            true_count += 1
            ml_pie['True News'] = true_count

    return ml_pie

# Compiles data from the 'Calculation_Table' where source is from Twitter into a dictionary which is returned:
    # {'Fake News': #, 'True News': #}
# Takes curr + conn (for connecting to database)
def mlClassificationTwitterData(cur, conn):
    cur.execute('SELECT source_id FROM Sources WHERE source_name = "Twitter"')
    source_id = cur.fetchone()[0]
    cur.execute('SELECT ml_classification FROM Calculation_Table WHERE source_id = "{}"'.format(source_id))
    ml_classification_list = list(cur.fetchall())
    ml_pie = {}

    fake_count = 0
    true_count = 0

    for i in ml_classification_list:

        classification = i[0]

        if classification == 0:
            fake_count += 1 
            ml_pie['Fake News'] = fake_count

        else: 
            true_count += 1
            ml_pie['True News'] = true_count

    return ml_pie

# Compiles data from the 'Calculation_Table' where source is from NYT into a dictionary which is returned:
    # {'Fake News': #, 'True News': #}
# Takes curr + conn (for connecting to database)
def mlClassificationNYTData(cur, conn):
    cur.execute('SELECT source_id FROM Sources WHERE source_name = "The New York Times"')
    source_id = cur.fetchone()[0]
    cur.execute('SELECT ml_classification FROM Calculation_Table WHERE source_id = "{}"'.format(source_id))
    ml_classification_list = list(cur.fetchall())
    ml_pie = {}

    fake_count = 0
    true_count = 0

    for i in ml_classification_list:

        classification = i[0]

        if classification == 0:
            fake_count += 1 
            ml_pie['Fake News'] = fake_count

        else: 
            true_count += 1
            ml_pie['True News'] = true_count

    return ml_pie

# Compiles data from the 'Calculation_Table' where source is from WSJ into a dictionary which is returned:
    # {'Fake News': #, 'True News': #}
# Takes curr + conn (for connecting to database)
def mlClassificationWSJData(cur, conn):
    cur.execute('SELECT source_id FROM Sources WHERE source_name = "The Wall Street Journal"')
    source_id = cur.fetchone()[0]
    cur.execute('SELECT ml_classification FROM Calculation_Table WHERE source_id = "{}"'.format(source_id))
    ml_classification_list = list(cur.fetchall())
    ml_pie = {}

    fake_count = 0
    true_count = 0

    for i in ml_classification_list:

        classification = i[0]

        if classification == 0:
            fake_count += 1 
            ml_pie['Fake News'] = fake_count

        else: 
            true_count += 1
            ml_pie['True News'] = true_count

    return ml_pie


# This function takes in a connection to the database. It then uses a JOIN to create a new table for NYT
# articles and pulls the section_name and page that each article was printed on. For each unique section
# in our database table, it calculates the average page that an article of that section is printed on.
# The function returns a dictionary containing this information.
def calculateNYTPrintPageAvg(cur, conn):  
    cur.execute('SELECT section_name, print_page FROM NYT_Sections JOIN NYT_URL_Data ON NYT_Sections.section_id = NYT_URL_Data.section_id')
    section_page_tups = cur.fetchall()

    section_dict = {}

    # for each article section and article print page, fill the dictionary
    for tup in section_page_tups:
        section_name = tup[0]
        print_page = int(tup[1])

        if section_name not in section_dict:
            section_dict[section_name] = [print_page]
        else:
            section_dict[section_name].append(print_page)
    
    conn.commit()

    return {section: statistics.mean(section_dict[section]) for section in section_dict}

# This function takes as input the data calculated in calculateNYTPrintPageAvg() and creates a 
# bar chart using plotly.
def visualizeNYTPrintPageAvg(section_average_dict):
    
    labels = list(section_average_dict.keys())    
    values = list(section_average_dict.values())
    data = [go.Bar(
        x = labels,
        y = values
    )]
    fig = go.Figure(data=data)
    fig.update_traces(marker_color='rgb(35,199,172)')
    fig.show()

# This function takes a connection to the database as input. For each of the 4 tables in the database
# containing article content, it does a JOIN with the sources table to get the source name and then adds
# one to an accumulator for that source, tracking the total number of articles in the database for each source.
# It then returns a dictionary containing all sources that have more than 2 articles.
def countNumArticlesPerSource(cur, conn):
    cur.execute('SELECT source_name FROM Sources JOIN NYT_URL_Data ON NYT_URL_Data.source_id = Sources.source_id')
    nyt_tups = cur.fetchall()

    cur.execute('SELECT source_name FROM Sources JOIN News_API ON News_API.SourceId = Sources.source_id')
    news_api_tups = cur.fetchall()

    cur.execute('SELECT source_name FROM Sources JOIN Twitter ON Twitter.SourceId = Sources.source_id')
    twitter_tups = cur.fetchall()

    cur.execute('SELECT source_name FROM Sources JOIN WSJ_URL_Data ON WSJ_URL_Data.source_id = Sources.source_id')
    wsj_tups = cur.fetchall()

    all_source_tups = nyt_tups + news_api_tups + twitter_tups + wsj_tups
    

    source_count_dict = {}

    for tup in all_source_tups:
        source_name = tup[0]

        if source_name not in source_count_dict:
            source_count_dict[source_name] = 0
        source_count_dict[source_name] += 1

    good_dict = {}

    for source in source_count_dict:
        if source_count_dict[source] >= 2:
            good_dict[source] = source_count_dict[source]

    return good_dict

# Takes as input a dictionary calculated in countNumArticlesPerSource() and puts all of this 
# information into a bar chart using plotly
def visualizeNumArticlesPerSource(source_count_dict):
    labels = list(source_count_dict.keys())    
    values = list(source_count_dict.values())
    data = [go.Bar(
        x = labels,
        y = values
    )]
    fig = go.Figure(data=data)
    fig.update_traces(marker_color='rgb(35,199,172)')
    fig.show()


# This function takes as input a connection to the database. For each headline URL in the WSJ table
# it checks wether the string ‘trump’ was in that headline. It returns a dictionary with two keys, one is
# Trump Headlines and the other is Non-Trump Headlines, where each key has an associated value which
# is a count.
def countPercentageTrumpWSJHeadlines(cur, conn):
    cur.execute('SELECT url_extension FROM WSJ_URL_Data')
    lst_urls = cur.fetchall()
    
    trump_dict = {'Trump Headlines': 0, 'Non-Trump Headlines': 0}

    for url_tup in lst_urls:
        url = url_tup[0]
        
        if 'trump' in url:
            trump_dict['Trump Headlines'] += 1
        else:
            trump_dict['Non-Trump Headlines'] += 1

    return trump_dict



# Utilizing the plotly library, this function creates a pie chart
# with the percentage of Fake News and True News
# Takes a dictionary as a paramater
def visualizations(dictionary):
    colors = ['#23c7ac', '#37474f']
    labels = list(dictionary.keys())    
    values = list(dictionary.values())
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
    fig.update_traces(textfont_size=20,
                  marker=dict(colors=colors, line=dict(color='#333', width=1)))

    fig.show()


cur, conn = setUpDatabase('finalProject.db')

trumpDict = countPercentageTrumpWSJHeadlines(cur, conn)
visualizations(trumpDict)

source_count_dict = countNumArticlesPerSource(cur, conn)
visualizeNumArticlesPerSource(source_count_dict)

section_avg_dict = calculateNYTPrintPageAvg(cur, conn)
visualizeNYTPrintPageAvg(section_avg_dict)

all_data = mlClassificationData(cur, conn)
visualizations(all_data)

twitter_data = mlClassificationTwitterData(cur, conn)
visualizations(twitter_data)

nyt_data = mlClassificationNYTData(cur, conn)
visualizations(nyt_data)

wsj_data = mlClassificationWSJData(cur, conn)
visualizations(wsj_data)


# Takes an output file name as input along with a connection to the database.
# Writes all of the calculations neatly formatted into the output_file.txt
def writeCalculations(output_file, cur, conn):
    with open(output_file, 'w') as outfile:
        outfile.write('FINAL PROJECT CALCULATION\n')
        outfile.write('Grant Ho and Chase Goldman\n\n')

        outfile.write('\n\nCALCULATION 1: For each article in our database, is it real news or fake news?\n\n')

        # real / fake news sections
        outfile.write('FAKE NEWS / REAL NEWS CLASSIFICATION FOR ALL ARTICLES: \n')
    
        cur.execute('SELECT source_name, article_id, ml_classification FROM Sources JOIN Calculation_Table WHERE Sources.source_id = Calculation_Table.source_id')
        classification_tups = cur.fetchall()

        for tup in classification_tups:
            source_name = tup[0]
            article_id = tup[1]
            classification = "FAKE NEWS" if tup[2] == 0 else "REAL NEWS"
            outfile.write('{} Article Number: {}\n'.format(source_name, article_id))
            outfile.write('\tClassification: {}\n\n'.format(classification))

        
        # section page output
        outfile.write('\n\nCALCULATION 2: On average, what page of the newspaper was each article from the New York Times sections in our database printed on?\n\n')
        
        for section in section_avg_dict:
            section_name = section
            average_page = section_avg_dict[section_name]

            outfile.write('On average, a New York Times article belonging to the {} Section was printed on page {} of the newspaper.\n'.format(section_name, average_page))

        # articles per source
        outfile.write('\n\nCALCULATION 3: For each source in the database with more than 2 articles, how many articles did we have from that source?\n\n')
    
        for source in source_count_dict:
            outfile.write('Source Name: {}\n'.format(source))
            outfile.write('Number of articles from {}: {}\n\n'.format(source, source_count_dict[source]))

        # percentage of trump hedalines
        outfile.write('\n\nCALCULATION 4: What percentage of Wall Street Journal Headlines involved Donald Trump?\n\n')
        cur.execute('SELECT url_extension FROM WSJ_URL_Data')
        lst_urls = cur.fetchall()

        trump_count = 0
        total_count = 0
        for url_tup in lst_urls:
            url = url_tup[0]
            trump = 'trump' in url

            if trump:
                trump_count += 1
            
            total_count += 1

            outfile.write('Wall Street Journal Article URL: {}\n'.format(url))
            outfile.write('\tDoes the URL headline include Trump: {}\n\n'.format('YES' if trump else 'NO'))

        outfile.write('\n\nFINAL PERCENTAGE: {}\n'.format(float(trump_count) / total_count * 100))
        outfile.write('\nOf all the WSJ headlines in our database, {}\% of them were about Donald Trump\n\n'.format(float(trump_count) / total_count * 100))


writeCalculations('finalOutput.txt', cur, conn)