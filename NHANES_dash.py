
from streamlit_option_menu import option_menu
import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import json
from bs4 import BeautifulSoup
import pandas as pd
import datetime 
import random
# Import date class from datetime module
from datetime import date
import matplotlib.pyplot as plt
from wordcloud import WordCloud

import pytrends
from pytrends.request import TrendReq

import tweepy
import praw
import datetime
import config

##################Reddit_AUTH#########################
# username = config.reddit_username
# password = config.reddit_reddit_password
# clientid = config.reddit_reddit_clientid
# clientsecret = config.reddit_clientsecret

username = st.secrets["reddit_username"]
password = st.secrets["reddit_password"]
clientid = st.secrets["reddit_clientid"]
clientsecret = st.secrets["reddit_clientsecret"]

#################Twitter_AUTH##########################
# API_Key = config.twitter_API_Key 
# API_Key_Secret = config.twitter_API_Key_Secret 
# Bearer_Token = config.twitter_Bearer_Token 
# Access_Token = config.twitter_Access_Token
# Access_Token_Secret = config.twitter_Access_Token_Secret

API_Key = st.secrets["twitter_API_Key"]
API_Key_Secret = st.secrets["twitter_API_Key_Secret"]
Bearer_Token = st.secrets["twitter_Bearer_Token"]
Access_Token = st.secrets["twitter_Access_Token"]
Access_Token_Secret = st.secrets["twitter_Access_Token_Secret"]

###################Database_AUTH#########################
# host= config.host
# user= config.user
# db_password= config.password
# port = config.port
# database = config.database

host= st.secrets["host"]
user= st.secrets["user"]
db_password= st.secrets["password"]
port = st.secrets["port"]
database = st.secrets["database"]

################################################################################################################

#Twitter API Authentication
consumerKey = API_Key
consumerSecret = API_Key_Secret
accessToken = Access_Token
accessTokenSecret = Access_Token_Secret
auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
auth.set_access_token(accessToken, accessTokenSecret)
api = tweepy.API(auth,wait_on_rate_limit=True)

#Reddit API Authentication
reddit = praw.Reddit(client_id=clientid,
                     client_secret=clientsecret,
                     password=password,
                     user_agent='Reddit search data extractor by /u/' + username + '',
                     username=username)

################################################################################################################
import pickle as pkle
import os.path

from streamlit_server_state import server_state, server_state_lock

import requests
import streamlit.components.v1 as components

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


st.set_page_config(page_title="Multipage_App", page_icon="", layout="wide")


with st.sidebar:
    choose = option_menu("Dash Menu", ["About the Project", "Google Trends", "NHANES",  "Reddit Conversations", "Twitter Conversations"],
                         icons=['house','google', 'graph-up','reddit', 'twitter'],
                         menu_icon="cast", default_index=0,
                         styles={
        "container": {"padding": "5!important", "background-color": "#fafafa"},
        "icon": {"color": "black", "font-size": "25px"}, 
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#636EFA"},
    }
    )


if choose == "About the Project":
#Add the cover image for the cover page. Used a little trick to center the image
    col1, col2, col3 = st.columns((.1,1,.1))

    with col1:
        st.write("")

    with col2:
        st.markdown(" <h1 style='text-align: center;'> NHANES, Health Disparities Data Visualization Tool</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'><i><b>Transformative Research to Address Health Disparities and Advance Health Equity at Minority Serving Institutions</b></i></p>", unsafe_allow_html=True)
        st.markdown("<center><img src='https://github.com/kkrusere/Market-Basket-Analysis-on-the-Online-Retail-Data/blob/main/Assets/MBA.jpg?raw=1' width=600/></center>", unsafe_allow_html=True)

    with col3:
        st.write("")

    col1, col2 = st.columns( [0.8, 0.2])
    with col1:               # To display the header text using css style
        st.markdown("About the Project:")

        st.markdown("""
                Design and Development of an MVP (minimum viable product) Data Visualization tool that provides stockholders with the Access and Ability to Track, Monitor and aid Data Driven Decisions with Regards to Health Disparities (and related topics) 
                
                ##### **Abstract**

                The subjects of Health disparities and inequities, health outcomes, health insurance, health system, and health equity hardly come up together in public discourse, but the relationships between these subjects cannot be denied, there is no one without the others. To reduce health disparities and inequities you must look at the other three, and the same goes if you want to improve health outcomes, you must look at the other three. The umbrella term that encompasses the different variables which influence the above subjects is “social determinates of health”. This is defined as the factors apart from the actual medical care which determine an individual’s access to healthcare (9,10,16). Often than not, when these subjects surface in public discourse, the conversations are highly politicized and the result is people taking and siding with whatever position that their political base takes without due diligence and some research of their own into the subject matter (6). Furthermore, in this digital information age (riddled with disinformation and misinformation), researching the subject matter is not as easy as you would think. You need to know what you are looking for and you are going to need specialized technical expertise to be able to pore through the data yourself. In this research paper, we investigate health disparities and the related topics. We investigate why these health disparities and inequities exist, and what is being done or what can be done to reduce these inequities. We then introduce a centralized, interactive, and responsive data visualization tool that allows the users to visualize data from the NIH’s NHANES (National Health and Nutrition Examination Survey) data (particular the Demographic and Questionnaire data which does look into the Social determinants of Health factors), keyword search trend demand visualization of the subject matter from Google Trends, and lastly access to and sentiment analysis of conversation of the subject matter on social platforms Twitter and Reddit. The objective of this is to shed light on the subject matter and provide tracking and monitoring capabilities to the general public and public health stakeholders, without the need for specialized technical expertise and resources. This in turn would aid them in making data driven decisions.
                
        """)

        st.markdown("##### ***Project Contributors:***")
        st.markdown("Kuzi Rusere")
        

elif choose == "Google Trends":
    col1, col2 = st.columns( [0.8, 0.2])
    with col1:               # To display the header text using css style
        st.markdown(""" <style> .font {
        font-size:35px ; font-family: 'Cooper Black'; color: black;} 
        </style> """, unsafe_allow_html=True)
        st.markdown('<p class="font">Google Trends</p>', unsafe_allow_html=True)
    keywords = ["Health disparities"] # this is going to be our keyword 

    #hl is the host language, 
    #tz is the time zone and 
    # retries is the number of retries total/connections/read all represented by one scalar
    pytrend = TrendReq(hl = 'en-US', tz = 0, retries=10)

    @st.cache(suppress_st_warning=True)
    def get_trend_suggested_keyword(string_kw):
        """  
        This fuction returns the google trends suggested keyword
        """
        try:
            KEYWORD = pytrend.suggestions(keyword=string_kw)[0]['mid']
        except:
            KEYWORD = string_kw

        return KEYWORD

    @st.cache(suppress_st_warning=True)
    def create_date_interval(time_interval):
        """
        This fuction creates the date interval needed for as one of the parameters for the pytrend.build_payload fuction
        The function takes in the important date and returns a string of the date interval - 30 days to the current date - 1 day  
        """
        start_date = date.today() - datetime.timedelta(days= time_interval)
        end_date = date.today() - datetime.timedelta(days= 3)

        x = (str(start_date)).split()[0]
        y = (str(end_date)).split()[0]

        #print(f"The start date is: {start_date} and the end date is: {end_date}")
        
        date_interval = f"{x} {y}"

        return date_interval

    @st.cache(allow_output_mutation=True)
    def wordcloud_of_related_queries(df, title):
        tuples = [tuple(x) for x in df.values]
        wordcloud = WordCloud(background_color ='white', min_font_size = 10).generate_from_frequencies(dict(tuples))
        fig,ax = plt.subplots()
        ax.imshow(wordcloud)
        ax.axis('off')
        ax.set_title(title,
                    fontsize = 10,
                    fontname="sans-serif", 
                    bbox=dict(boxstyle = "square",facecolor = "white"))

        return fig
    
    @st.cache(suppress_st_warning=True)
    def get_top_and_rising(related_queries_dict):
        """  
        This fuction returns the top and rising related queries 
        """
        # for rising related queries
        related_queries_rising = related_queries_dict.get('rising')
        # for top related queries
        related_queries_top = related_queries_dict.get('top')

        return related_queries_rising, related_queries_top            
        
    @st.cache(allow_output_mutation=True, ttl=18000)
    def get_trends(keyword, time_interval):
        """
        Returns: 
            Interest overtime dataframe = Google_trends_df
            Top & Rising Related Queries
            Top & Rising Related Topics
            Interest by Region 
        """

        #setting up the parameters for the payload
        KEYWORDS=[keyword]
        DATE_INTERVAL= create_date_interval(time_interval)
        COUNTRY="US" 
        CATEGORY = 0 
        SEARCH_TYPE=''

        #the below is building the payload using the above parameters
        pytrend.build_payload( kw_list= KEYWORDS, timeframe = DATE_INTERVAL, geo = COUNTRY, cat=CATEGORY,gprop=SEARCH_TYPE) 
        df = pytrend.interest_over_time() #we will  assign the interest_overtime/trends dataframe to df

        #now we will rename the column name from the pytrends suggested mid value to the actual name of the high profile person and chronic condition 
        Google_trends_df = df.rename(columns={KEYWORDS[0]: keyword})
        Google_trends_df.drop('isPartial', axis=1, inplace=True)
        Google_trends_df.reset_index(inplace = True)



        #####################################################################

        related_queries = pytrend.related_queries()
        related_queries[keyword] = related_queries.pop(KEYWORDS[0])

        Google_trends_df_related_queries_rising, Google_trends_df_related_queries_top = get_top_and_rising(related_queries[keyword])

        #########################################################################
        related_topics = pytrend.related_topics()
        related_topics[keyword] = related_topics.pop(KEYWORDS[0])
        Google_trends_df_related_topics_rising, Google_trends_df_related_topics_top = get_top_and_rising(related_topics[keyword])
        Google_trends_df_related_topics_rising = Google_trends_df_related_topics_rising.drop(["formattedValue", "link", "topic_mid","topic_type"], axis = 1)
        Google_trends_df_related_topics_top = Google_trends_df_related_topics_top.drop(["formattedValue", "hasData","link", "topic_mid","topic_type"], axis = 1)

        ##########################################################################################################################

        Google_trends_df_region = pytrend.interest_by_region() #'DMA' returns Metro level data
        #now we will rename the column name from the pytrends suggested mid value to the actual name of the high profile person and chronic condition 
        Google_trends_df_region.reset_index(inplace=True)
        Google_trends_df_region = Google_trends_df_region.rename(columns={'geoName':'State',KEYWORDS[0]: keyword})

        return Google_trends_df, Google_trends_df_related_queries_rising, Google_trends_df_related_queries_top, Google_trends_df_region,  Google_trends_df_related_topics_rising, Google_trends_df_related_topics_top

    @st.cache(allow_output_mutation=True, ttl=18000)
    def get_trend_overtime(keywords, date_interval):
        """
        This fuction reads in a list of keywords and returns the interest overtime dataframe
        """

        comp_keywords = keywords
        KEYWORDS= comp_keywords
        DATE_INTERVAL= create_date_interval(date_interval)
        COUNTRY="US" 
        CATEGORY = 0 
        SEARCH_TYPE=''
        #######################
        #the below is building the payload using the above parameters
        pytrend.build_payload( kw_list= KEYWORDS, timeframe = DATE_INTERVAL, geo = COUNTRY, cat=CATEGORY,gprop=SEARCH_TYPE) 
        df = pytrend.interest_over_time() #we will  assign the interest_overtime/trends dataframe to df


        
        df.drop('isPartial', axis=1, inplace=True)
        df.columns = keywords
        df.reset_index(inplace=True)

        return df


    ######################################################################
    #this is to allow the users to change the time interval for the google trends 
    decode_days = {"30 Days": 30,
                    "60 Days": 60,
                    "90 Days": 90,
                    "12 Months": 365,
                    "5 Years": 1825}

    date_interval_choice = ["30 Days",
                            "60 Days",
                            "90 Days",
                            "12 Months",
                            "5 Years"]
    row_space1, row_1, row_space2, row_2, row_space3 = st.columns((.1, 1, .1, 1, .1))

    with row_1:                        
        option = st.selectbox(
            "Please select the date range for the Google Trend",
            (date_interval_choice))
    day = option
    date_interval = decode_days.get(option)

    ######################################################################

    Google_trends_df, Google_trends_df_related_queries_rising, Google_trends_df_related_queries_top, Google_trends_df_region,  Google_trends_df_related_topics_rising, Google_trends_df_related_topics_top = get_trends(keywords[0], date_interval)
    ############################################################



    ################Google Trends visuals############################################
    row0_1, row0_2, = st.columns(2)

    with row0_1:
        #interest over time 
        fig = px.line(Google_trends_df, x="date", y= Google_trends_df["Health disparities"], title="Google Search Interest over time for Health disparities")

        st.plotly_chart(fig, use_container_width=True)

    with row0_2:
        x = wordcloud_of_related_queries(Google_trends_df_related_queries_top, f"Wordcloud of related quiries in the time interval {option}")
        st.pyplot(x, use_container_width=True )

    row1_1, row1_2 = st.columns(2)

    with row1_1:
        if len(Google_trends_df_related_topics_top)>=20:
            fig = make_subplots(rows=1, cols=2, subplot_titles=("Top 10 related Topics", "Bottom 10 related Topics"))
            df1 = Google_trends_df_related_topics_top.head(10)
            df2 = df = Google_trends_df_related_topics_top.tail(10)


            fig.add_trace(
                go.Bar(name = "Top 10 related Topics",x=df1["value"], y=df1["topic_title"], text=df1["topic_title"], orientation='h', marker_color="#636EFA"),
                    row=1, col=1
            )

            fig.add_trace(
                go.Bar(name= "Bottom 10 related Topics", x=df2["value"], y=df2["topic_title"], text=df2["topic_title"], orientation='h', marker_color="#636EFA"),
                row=1, col=2
            )
            fig.update_yaxes(visible=False, showticklabels=False)


            fig.update_layout(height=500,width=1070, title_text="Google Trends Related Topics")
            fig.update_layout(showlegend=False)
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)



        else:
            df = Google_trends_df_related_topics_top.head(10)
            x=df["value"]
            y=df["topic_title"]
            text=df["topic_title"]

            # Use textposition='auto' for direct text
            fig = go.Figure(data=[go.Bar(
                        x=x, y=y,
                        text=text,
                        orientation='h', marker_color="#636EFA"
                    )])
            fig.update_yaxes(visible=False, showticklabels=False)
            fig.update_layout(title_text="Google Trends Related Topics")
            fig.update_layout(hovermode='x unified')

            st.plotly_chart(fig, use_container_width=True)




    with row1_2:
        #interest per subregion 
        df_region = Google_trends_df_region.copy()
    
        df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2011_us_ag_exports.csv')
        state_ccode_dict = dict(zip(df["state"], df["code"]))
        state_ccode_dict["District of Columbia"] = "DC"

        df_region["code"] = df_region["State"].apply(lambda x:state_ccode_dict.get(x))


        fig = go.Figure(data=go.Choropleth(
            locations=df_region['code'], # Spatial coordinates
            z = df_region['Health disparities'].astype(float), # Data to be color-coded
            locationmode = 'USA-states', # set of locations match entries in `locations`
            colorscale = "bluered",
            colorbar_title = "Google Search volume index",
            text = df_region['State'],
        ))

        fig.update_layout(
        
            title_text = f"Google Search Trend for {df.columns[1]} over {day}",
            geo_scope='usa', # limite map scope to USA
        )
        fig.update_geos(visible=True)


        st.plotly_chart(fig, use_container_width=True)


    keywords_ = ["Health Disparities", "Health Equity", "Health Outcomes", "Healthcare System", "Health Insurance"]
    df = get_trend_overtime(keywords_, date_interval)

    df = df.set_index('date')
    df = df.unstack().reset_index(name='value')
    df.rename(columns={'level_0': 'keyword'}, inplace=True)


    fig = px.line(df, x="date", y="value", color='keyword')
    fig.update_layout(hovermode='x unified')
    fig.update_layout(width=1500,title_text="Google Trends Interest overtime of subject matter related Topics")
    st.plotly_chart(fig, use_container_width=True)


    st.markdown("---")
    ######################################################################




elif choose == "NHANES":
    #Add a file uploader to allow users to upload their project plan file
    st.markdown(""" <style> .font {
    font-size:35px ; font-family: 'Cooper Black'; color: black;} 
    </style> """, unsafe_allow_html=True)
    st.markdown('<p class="font">NHANES</p>', unsafe_allow_html=True)
    st.write("this is the NHANES")
    #creating a list of the survey cycles that we are going to be collecting the data
    cycle_list = list()
    a = 1999
    b = 2000
    for i in range(10):
        cycle_list.append(f"{a}-{b}")
        a = b + 1
        b = b + 2
    #Demography variable URL from the NHANES
    demographics_url = "https://wwwn.cdc.gov/nchs/nhanes/search/variablelist.aspx?Component=demographics"

    def get_variable_df(url, cycle_list = cycle_list):
        """
        This fuction inputs the NHANES URL for Variable list 
        The Pandas' pandas.read_html() fuction is used to read tables on the URL
        Resulting data frame is then cleaned (adding a year column and removing some other columns not needed)
        Year column matches the survey cycle periods
        Cycle list is used to filter the data to just the cycle of interest 
        Returns the data frame of the variable  
        """
        dfs = pd.read_html(url)
        df = dfs[0] #the table of interest in on the index 0

        Years = [i for i in  range(len(df))]
        df["Years"] = Years 
        for i in range(len(df)):
            x = df['Begin Year'][i]
            y = df['EndYear'][i]
            df["Years"][i] = f"{x}-{y}"
        df.drop(["Begin Year", "EndYear", "Component","Use Constraints"], axis=1, inplace=True)
        df = df.loc[df["Years"].isin(cycle_list)]
        df.reset_index(drop=True, inplace=True)

        return df

    def check_variable(data_frame):
        """
        This fuction look at the variables if they are in all cycles or not 
        If the variable is present in all 10 cycles append it to a list for later use
        """
        variable_list = list()
        new_list = list((dict(data_frame['Variable Name'].value_counts())).keys())
        for i in range(len(new_list)):
            temp = data_frame[data_frame["Variable Name"] == f"{new_list[i]}"]
            temp = temp.reset_index(drop=True)
            if temp.shape[0] > 5:#the variable has to be in all the years that we are looking at
                variable_list.append(new_list[i])
        
        
        return variable_list



    #we call the get_variable_df fuction for the demography URL
    demographics_var_df = get_variable_df(demographics_url)

    #so we check the variable in the demography dataframe 
    variable_list = check_variable(demographics_var_df)

    #we are going to remove the below variable from the variable list as they are of no use here
    variable_list = [ele for ele in variable_list if ele not in ["RIDEXMON", "WTINT2YR", "SDMVSTRA", "RIDSTATR", "WTMEC2YR"]]

    #we use the variable list to filter the demography variable dataframe
    demographics_var_df =  demographics_var_df.loc[demographics_var_df["Variable Name"].isin(variable_list)]
    demographics_var_df.reset_index(drop=True, inplace=True)



    def get_variable_documentation(data_File_Name, cycle = cycle_list[0], variable_list = variable_list):
        """
        This fuction goes to the  NHANES Data Documentation for the input data_file_name with the help of BeautifulSoup
        Three dictionaries are created for the code table, sas label and the english text (variable explanation)
        The fuction then returns the dictionaries. 
        """
        url = f"https://wwwn.cdc.gov/Nchs/Nhanes/{cycle}/{data_File_Name}.htm"
        varibale_code_table = dict()
        variable_sas_label = dict()
        variable_English_Text = dict()
        
        req=requests.get(url)
        content=req.text
        soup = BeautifulSoup(content)

        mydivs = soup.find_all("div", {"class": "pagebreak"})
        for i, div in enumerate(mydivs):
            x = div.find_all_next()
            variable = x[0]["id"]
            if variable in variable_list:
                #print(variable)
                #print(f"{x[2].text}{x[3].text}")
                variable_sas_label[variable] = x[5].text
                #print(f"{x[4].text}{x[5].text}")
                variable_English_Text[variable] = {x[7].text}
                #print(f"{x[6].text}{x[7].text}")
                if div.find("table") is not None:
                    table = pd.read_html(str(div.find('table')))[0]
                    varibale_code_table[variable] = table
                    #print(data_frame[i-1])
            #print("#####################")

        return varibale_code_table, variable_sas_label, variable_English_Text


    #code we will call the get_variable_documentation fuction 
    demography_varibale_code_table, demography_variable_sas_label, demography_variable_English_Text = get_variable_documentation("DEMO")



    questionnaire_url = "https://wwwn.cdc.gov/nchs/nhanes/search/variablelist.aspx?Component=questionnaire"
    questionnaire_var_df = get_variable_df(questionnaire_url)
    questionnaire_var_df.drop(questionnaire_var_df[questionnaire_var_df['Data File Name'] == "OCQ_H_R"].index, inplace = True)
    questionnaire_var_df.reset_index(drop=True, inplace=True)


    questionnaire_data_file_list = list()
    for string_key in list(questionnaire_var_df["Data File Description"].unique()):
        if string_key not in ["Dermatology",
                                'Blood Pressure & Cholesterol',
                                'Diet Behavior & Nutrition',
                                'Immunization',
                                'Kidney Conditions - Urology',
                                'Oral Health',
                                'Physical Functioning',
                                'Pesticide Use',
                                'Smoking - Household Smokers',
                                'Weight History',
                                'Respiratory Health',
                                'Sexual Behavior',
                                'Diabetes',
                                'Drug Use',
                                'Reproductive Health',
                                'Consumer Behavior',
                                'Food Security',
                                "Sexual Behavior - Youth", 
                                "Acculturation", 
                                "Alcohol Use",
                                "Audiometry", 
                                "Prescription Medications",
                                "Cardiovascular Health", 
                                "Early Childhood"]:
            a = len(questionnaire_var_df[questionnaire_var_df["Data File Description"] == string_key]["Years"].value_counts())
            if a >=9 or string_key in ["Respiratory Health","Consumer Behavior","Income"]:
                questionnaire_data_file_list.append(string_key)


    #Now that we have this data file list, we can go through it file name by file name selecting the variable that of more interest to this project 
    def return_temp_df(data_File_Name):
        """
        This fuction filters the questionnaire_var_df using the input data file name and returns the resulting dataframe
        """
        print(f"The data frame is for {data_File_Name}")
        df = questionnaire_var_df[questionnaire_var_df["Data File Description"] == data_File_Name]
        df.reset_index(drop= True, inplace=True)
        return df

    variable_documentation_dict = dict() #the keys will be the Data Category names
    #so we will add the Demography variable information first
    variable_documentation_dict["Demography"] = [variable_list, demography_variable_sas_label,demography_variable_English_Text,demography_varibale_code_table]


    for i, the_name in enumerate(questionnaire_data_file_list):
        df = return_temp_df(the_name)
        q_variable_list = check_variable(df)
        x,y,z = get_variable_documentation(df["Data File Name"][0], cycle=df["Years"][0], variable_list = q_variable_list)
        variable_documentation_dict[f"{the_name}"] = [q_variable_list, y,z,x]


    merged_df = pd.read_csv("merged_data.csv")

    col1, col2 = st.columns(2)
    with col1:
        def value_mapper(x):
            df = variable_documentation_dict['Demography'][3]["RIAGENDR"]
            i = df[df['Code or Value'] == str(x)].index[0]
            return df['Value Description'][i]
        tempdf = pd.DataFrame(merged_df["Gender"].value_counts())
        tempdf.reset_index(inplace= True)
        tempdf.columns = ["Gender", "Count"]
        tempdf['Gender'] = tempdf['Gender'].astype(int)
        tempdf['Gender'] = tempdf['Gender'].astype(str)
        tempdf['Gender'] = tempdf['Gender'].apply(value_mapper)
        fig = px.pie(tempdf, values='Count', names='Gender')
        st.plotly_chart(fig)
    with col2:
        #we will create a helper fuction 
        def value_mapper(x):
            df = variable_documentation_dict['Health Insurance'][3]["HIQ011"]
            i = df[df['Code or Value'] == str(x)].index[0]
            return df['Value Description'][i]
        


        tempdf = pd.DataFrame(merged_df["Covered by health insurance"].value_counts())
        tempdf.reset_index(inplace= True)
        tempdf.columns = ["Covered by health insurance", "Count"]
        tempdf['Covered by health insurance'] = tempdf['Covered by health insurance'].astype(int)
        tempdf['Covered by health insurance'] = tempdf['Covered by health insurance'].astype(str)
        tempdf['Covered by health insurance'] = tempdf['Covered by health insurance'].apply(value_mapper)
        fig = px.bar(tempdf, x="Covered by health insurance", y="Count")
        st.plotly_chart(fig)


    col1, col2 = st.columns(2)
    with col1:
        #we will create a helper fuction 
        def value_mapper(x):
            df = variable_documentation_dict['Hospital Utilization & Access to Care'][3]["HUQ030"]
            i = df[df['Code or Value'] == str(x)].index[0]
            return df['Value Description'][i]
            


        tempdf = pd.DataFrame(merged_df["Routine place to go for healthcare"].value_counts())
        tempdf.reset_index(inplace= True)
        tempdf.columns = ["Routine place to go for healthcare", "Count"]
        tempdf['Routine place to go for healthcare'] = tempdf['Routine place to go for healthcare'].astype(int)
        tempdf['Routine place to go for healthcare'] = tempdf['Routine place to go for healthcare'].astype(str)
        tempdf['Routine place to go for healthcare'] = tempdf['Routine place to go for healthcare'].apply(value_mapper)
        fig = px.bar(tempdf, x="Routine place to go for healthcare", y="Count")
        st.plotly_chart(fig)

    with col2:
        pass
##################################################################################################

elif choose == "Reddit Conversations":
    st.markdown(""" <style> .font {
    font-size:35px ; font-family: 'Cooper Black'; color: black;} 
    </style> """, unsafe_allow_html=True)
    st.markdown('<p class="font">Reddit Conversations</p>', unsafe_allow_html=True)


    search_terms =  ['"Health Disparities"','"Health Equity"', '"Health Insurance"', '"Health Outcomes"', '"Healthcare System"']

    reddit_df_HD = pd.read_csv('reddit_"Health Disparities"_data.csv')
    reddit_df_HE = pd.read_csv('reddit_"Health Equity"_data.csv')
    reddit_df_HI = pd.read_csv('reddit_"Health Insurance"_data.csv')
    reddit_df_HO = pd.read_csv('reddit_"Health Outcomes"_data.csv')
    reddit_df_HS = pd.read_csv('reddit_"Healthcare System"_data.csv')

    dataframe_list = [reddit_df_HD,reddit_df_HE,reddit_df_HI,reddit_df_HO,reddit_df_HS]
    the_data = dict(zip(search_terms,dataframe_list))

    #############################################################

    def Reddit(link):
        src = '<iframe id="reddit-embed" src="https://www.redditmedia.com{}?ref_source=embed&amp;ref=share&amp;embed=true" sandbox="allow-scripts allow-same-origin allow-popups" style="border:  inset;" height="400" width="500" scrolling="yes"></iframe>'.format(link)
        components.html(src, width=None, height=500, scrolling=True)

    analyzer = SentimentIntensityAnalyzer()


    def senti_analyze(text):
        result = analyzer.polarity_scores(text)
        sentiment = result["compound"]
        if sentiment == 0:
            return "neu"
        elif sentiment < 0:
            return "neg"
        else:
            return "pos"

    sentiment_emoji_dict = {
        "neu": ":neutral_face:",
        "neg": ":rage:",
        "pos":":relieved:"
    }

    def for_pychart(df):
        df["sentiment"] = df["Title"].apply(senti_analyze)

        tem_df = pd.DataFrame(df["sentiment"].value_counts()).reset_index()
        tem_df.columns = ["sentiment", "sentiment_count"]
        fig = px.pie(tem_df, 
                    values='sentiment_count', 
                    names='sentiment',
                    title='Sentiment Score percentage of the total Reddit Topics',
                    color='sentiment',
                    color_discrete_map={'pos':'green',
                                        'neu':'yellow',
                                        'neg':'red'})
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        return fig

    #############################################################


    choice = search_terms[0]

    if os.path.isfile('Rnext.p'):
        next_clicked = pkle.load(open('Rnext.p', 'rb'))
        choice = search_terms[next_clicked]
        if next_clicked == len(search_terms):
            
            next_clicked = 0 
    else:
        next_clicked = 0 

    if next:
        next_clicked = next_clicked+1
        if next_clicked == len(search_terms):
            next_clicked = 0 


    col1, col2, col3, col4,col5 = st.columns([.2,.2,.2,.2,.63])
    with col1:
        if st.button(f"{search_terms[0]}"):
            choice = search_terms[0]
            comment_count = 0
            pkle.dump(comment_count, open('commennext.p', 'wb'))
            with server_state_lock.count:
                server_state.count = 0
    with col2:
        if st.button(f"{search_terms[1]}"):
            choice = search_terms[1]
            with server_state_lock.count:
                server_state.count = 0
    with col3:
        if st.button(f"{search_terms[2]}"):
            choice = search_terms[2]
            comment_count = 0
            pkle.dump(comment_count, open('commennext.p', 'wb'))
            with server_state_lock.count:
                server_state.count = 0
    with col4:
        if st.button(f"{search_terms[3]}"):
            choice = search_terms[3]
            comment_count = 0
            pkle.dump(comment_count, open('commennext.p', 'wb'))
            with server_state_lock.count:
                server_state.count = 0

    with col5:
        if st.button(f"{search_terms[4]}"):
            choice = search_terms[4]
            comment_count = 0
            pkle.dump(comment_count, open('commennext.p', 'wb'))
            with server_state_lock.count:
                server_state.count = 0
    pkle.dump(search_terms.index(choice), open('Rnext.p', 'wb'))


    st.markdown(choice)

    df = the_data.get(choice)

    ###################################################################

    with server_state_lock["count"]:  # Lock the "count" state for thread-safety
        if "count" not in server_state:
            server_state.count = 0
        if server_state_lock.count == 0:
            server_state_lock.count = 0
            
    col1,col2,col3 = st.columns([.1,1,1])
    with col1:
        Prev = st.button("Prev")
        if Prev:
            if server_state.count == 0:
                with server_state_lock.count:
                    server_state.count = 0
            else:
                with server_state_lock.count:
                    server_state.count -= 1

    with col3:
        Next = st.button("Next")
        if Next:
            comment_count = 0
            pkle.dump(comment_count, open('commennext.p', 'wb'))
            with server_state_lock.count:
                server_state.count += 1

        st.markdown("Reddit Topics sentiment Analysis")
        st.write(f"{analyzer.polarity_scores(df['Title'][server_state.count])}")
        st.markdown(sentiment_emoji_dict.get(senti_analyze(df['Title'][server_state.count])))
        st.plotly_chart(for_pychart(df), use_container_width=True)



    with col2:
        if server_state.count >= 0:
            try:
                Reddit(df["permalink"][server_state.count])
            except Exception as e: 
                st.error("No Reddit post preview available")
                st.error(f"There was error: {e} ")
                st.markdown(
                f"""
                #### **Post from Subreddit: {df["subreddit"][server_state.count]}**
                {df["Title"][server_state.count]}
                """
                )
        elif server_state.count < 0:
            with server_state_lock.count:
                server_state.count = 0
            try:
                Reddit(df["permalink"][0])
            except Exception as e: 
                st.error("No Reddit post preview available")
                st.error(f"There was error: {e} ")
                st.markdown(
                f"""
                #### **Post from Subreddit: {df["subreddit"][server_state.count]}**
                {df["Title"][server_state.count]}
                """
                )
        submission = reddit.submission(id= df["id"][server_state.count])
        if os.path.isfile('commennext.p'):
            comm_next_clicked = pkle.load(open('commennext.p', 'rb'))
            comment_count = comm_next_clicked
            if comm_next_clicked == len(submission.comments.list()):
                comm_next_clicked = 0 
        else:
            comm_next_clicked = 0 
            comment_count = comm_next_clicked

        if len(submission.comments.list()) == 0:
            st.markdown("## There are no comments for this Post")
        else:
            x = submission.comments.list()[comment_count].body
            st.markdown("#### **Post Comments**")
            st.write(x)
            st.markdown("**Sentiment**")
            st.write(f"{analyzer.polarity_scores(x)}")
            st.markdown(sentiment_emoji_dict.get(senti_analyze(x)))

            if st.button("Next Comment"):
                comment_count+= 1
                if comment_count == len(submission.comments.list()):
                    comment_count = 0
                
        pkle.dump(comment_count, open('commennext.p', 'wb'))


    ##################################################################


    next = st.button('Back to Health Disparities')


##############################################################################


elif choose == "Twitter Conversations":
    st.markdown(""" <style> .font {
    font-size:35px ; font-family: 'Cooper Black'; color: black;} 
    </style> """, unsafe_allow_html=True)
    st.markdown('<p class="font">Twitter Conversations</p>', unsafe_allow_html=True)

    search_terms =  ['"Health Disparities"','"Health Equity"', '"Health Insurance"', '"Health Outcomes"', '"Healthcare System"']

    df_HD = pd.read_csv('"Health Disparities"_data.csv')
    df_HE = pd.read_csv('"Health Equity"_data.csv')
    df_HI = pd.read_csv('"Health Insurance"_data.csv')
    df_HO = pd.read_csv('"Health Outcomes"_data.csv')
    df_HS = pd.read_csv('"Healthcare System"_data.csv')

    dataframe_list = [df_HD,df_HE,df_HI,df_HO,df_HS]
    the_data = dict(zip(search_terms,dataframe_list))

    #############################################################

    def Tweet(id):
        api = f"https://publish.twitter.com/oembed?url=https://twitter.com/twitter/statuses/{id}"
        response = requests.get(api)
        res = response.json()
        res["width"] = 100
        res["height"] = 300
        res = response.json()["html"] 
        components.html(res,height= 700, scrolling=True)

    analyzer = SentimentIntensityAnalyzer()


    def senti_analyze(text):
        result = analyzer.polarity_scores(text)
        sentiment = result["compound"]
        if sentiment == 0:
            return "neu"
        elif sentiment < 0:
            return "neg"
        else:
            return "pos"

    sentiment_emoji_dict = {
        "neu": ":neutral_face:",
        "neg": ":rage:",
        "pos":":relieved:"
    }

    def for_pychart(df):
        df["sentiment"] = df["tweet"].apply(senti_analyze)

        tem_df = pd.DataFrame(df["sentiment"].value_counts()).reset_index()
        tem_df.columns = ["sentiment", "sentiment_count"]
        fig = px.pie(tem_df, 
                    values='sentiment_count', 
                    names='sentiment',
                    title='Sentiment Score percentage of the total Tweets',
                    color='sentiment',
                    color_discrete_map={'pos':'green',
                                        'neu':'yellow',
                                        'neg':'red'})
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        return fig
    #############################################################




    if os.path.isfile('next.p'):
        next_clicked = pkle.load(open('next.p', 'rb'))
        choice = search_terms[next_clicked]
        if next_clicked == len(search_terms):
            
            next_clicked = 0 
    else:
        next_clicked = 0 

    if next:
        next_clicked = next_clicked+1
        if next_clicked == len(search_terms):
            next_clicked = 0 


    col1, col2, col3, col4,col5 = st.columns([.2,.2,.2,.2,.3])
    with col1:
        if st.button(f"{search_terms[0]}"):
            choice = search_terms[0]
            with server_state_lock.count:
                server_state.count = 0
    with col2:
        if st.button(f"{search_terms[1]}"):
            choice = search_terms[1]
            with server_state_lock.count:
                server_state.count = 0
    with col3:
        if st.button(f"{search_terms[2]}"):
            choice = search_terms[2]
            with server_state_lock.count:
                server_state.count = 0
    with col4:
        if st.button(f"{search_terms[3]}"):
            choice = search_terms[3]
            with server_state_lock.count:
                server_state.count = 0

    with col5:
        if st.button(f"{search_terms[4]}"):
            choice = search_terms[4]
            with server_state_lock.count:
                server_state.count = 0
    pkle.dump(search_terms.index(choice), open('next.p', 'wb'))


    st.markdown(choice)

    df = the_data.get(choice)

    ###################################################################

    with server_state_lock["count"]:  # Lock the "count" state for thread-safety
        if "count" not in server_state:
            server_state.count = 0
        if server_state_lock.count == 0:
            server_state_lock.count = 0
            
    col1,col2,col3 = st.columns([.1,1,1])
    with col1:
        Prev = st.button("Prev")
        if Prev:
            if server_state.count == 0:
                with server_state_lock.count:
                    server_state.count = 0
            else:
                with server_state_lock.count:
                    server_state.count -= 1

    with col3:
        Next = st.button("Next")
        if Next:
            with server_state_lock.count:
                server_state.count += 1
        st.markdown("Tweet sentiment Analysis")
        st.write(f"{analyzer.polarity_scores(df['tweet'][server_state.count])}")
        st.markdown(sentiment_emoji_dict.get(senti_analyze(df['tweet'][server_state.count])))
        st.plotly_chart(for_pychart(df), use_container_width=True)


    with col2:
        if server_state.count >= 0:
            try:
                Tweet(df["id"][server_state.count])
            except:
                st.error("No Tweet preview available")
                st.markdown(
                f"""
                #### **Tweet from {df["name"][server_state.count]}**
                {df["tweet"][server_state.count]}
                """
                )
        elif server_state.count < 0:
            with server_state_lock.count:
                server_state.count = 0
            try:
                Tweet(df["id"][0])
            except:
                st.error("No Tweet preview available")
                st.markdown(
                f"""
                #### **Tweet from {df["name"][server_state.count]}**
                {df["tweet"][server_state.count]}
                """
                )
        
    ##################################################################


    next = st.button('Back to Health Disparities')   
