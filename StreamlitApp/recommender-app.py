import pandas as pd
import pymilvus
import streamlit as st

#st.set_page_config(layout="wide")
@st.cache_data
def load_data():
#    orig_data=pd.read_csv('DatasetEnglish.csv')
#    sentiment_data=pd.read_csv('sentiment_data.csv')
#    data_extra = pd.merge(orig_data, sentiment_data, how='left', on='talk_id')
#    data_extra=data_extra.drop('transcript', axis=1)
    data_extra=pd.read_csv('data_extra.csv')
    return data_extra

data_extra = load_data()

@st.cache_resource
def load_zilliz():
    pymilvus.connections.connect(uri=st.secrets["zilliz_uri"],
    token=st.secrets["zilliz_token"]
    )
    collection = pymilvus.Collection("CosineSimilarity")
    return collection

collection = load_zilliz()

st.title("TED Talks Recommender")

unique_topics = (data_extra['topic_0_name'].drop_duplicates()).sort_values()

selected_topics = st.multiselect("Filter by topic", unique_topics)

df = data_extra[data_extra["topic_0_name"].isin(selected_topics)]

selected_talk = st.selectbox("Select a talk", df['talk_title'])

if selected_talk is None:
    st.write("Please select a talk from the dropdown menu.")
else:
    st.write(f"You have selected: {selected_talk}")
    st.write(f"Speaker: {df[df['talk_title'] == selected_talk]['speakers_name'].values[0]}")
    st.write(f"Description: {df[df['talk_title'] == selected_talk]['talk_description'].values[0]}")

    @st.cache_data
    def get_top_5_sentiment(selected_talk):
        selected_score = df[df["talk_title"] == selected_talk]["text_polarity_score"].values[0]
        df["score_diff"] = abs(df["text_polarity_score"] - selected_score)
        filtered_df = df.sort_values(by="score_diff")
        top_sent = filtered_df[filtered_df["talk_title"] != selected_talk].head(5)
        return top_sent

    @st.cache_data 
    def get_top_5_cosine(selected_talk):
        talk_id = df[df["talk_title"] == selected_talk]["talk_id"].values[0]

        query_expr = f"talk_id == {talk_id}"

        results = collection.query(
            expr=query_expr,
            output_fields=["talk_id", "vector"]
        )

        query_vector = results[0]['vector']

        search_params = {
            "index_type": "AUTOINDEX",
            "metric_type": "COSINE",
            "params": {}
        }

        results = collection.search(
            data=[query_vector],
            anns_field="vector",
            param=search_params,
            limit=6,
            output_fields=["talk_id"]
        )

        result_talk_ids = [result.entity.talk_id for result in results[0][1:]]

        return result_talk_ids

    @st.cache_resource 
    def get_query_vector(selected_talk):
        talk_id = df[df["talk_title"] == selected_talk]["talk_id"].values[0]

        query_expr = f"talk_id == {talk_id}"

        results = collection.query(
            expr=query_expr,
            output_fields=["talk_id", "vector"]
        )

        query_vector = results[0]['vector']
        return query_vector

    query_vector = get_query_vector(selected_talk)

    def get_results(selected_talk):
        return get_top_5_sentiment(selected_talk), get_top_5_cosine(selected_talk)

    top_5_sent, top_5_cosine = get_results(selected_talk)

    
    container = st.container()
    output_sent = "" # initialize the variable
    output_cosine = "" # initialize the variable
    with container:
        col1, col2 = st.columns(2) # create two columns
        with col1: # use the first column
            # add both buttons in the first column
            if st.button("Get top 5 related talks by sentiment"): # add a button
                try:
                    top_5_sent = get_top_5_sentiment(selected_talk)
                    # store the output in a variable
                    output_sent = ""
                    output_sent += "Top 5 related talks based on sentiment score:\n"
                    for i in range(5):
                        related_talk = top_5_sent["talk_title"].iloc[i]
                        related_name = top_5_sent["speakers_name"].iloc[i]
                        url = top_5_sent["shortened_url"].iloc[i]
                        output_sent += f"{i+1}. {related_talk} by {related_name} URL: {url}\n"
                except IndexError:
                    output_sent = "Sorry, there are no related talks by sentiment for this talk."
            if st.button("Get top 5 related talks by cosine similarity"): # add another button
                top_5_cosine = get_top_5_cosine(selected_talk)
                # store the output in a variable
                output_cosine = ""
                output_cosine += "Top 5 related talks based on cosine similarity:\n"
                for i in range(5):
                    related_talk = data_extra[data_extra["talk_id"] == top_5_cosine[i]]["talk_title"].values[0]
                    related_name = data_extra[data_extra["talk_id"] == top_5_cosine[i]]["speakers_name"].values[0]
                    url = data_extra[data_extra["talk_id"] == top_5_cosine[i]]["shortened_url"].values[0]
                    output_cosine += f"{i+1}. {related_talk} by {related_name} URL: {url}\n"
        with col2: # use the second column
            # display both outputs in the second column
            st.write(output_sent)
            st.write(output_cosine)
