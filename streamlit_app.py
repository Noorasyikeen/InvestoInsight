import streamlit as st
import datetime
import pandas as pd
import numpy as np
from model import load_pretrained_model, make_predictions


curr_time_raw = datetime.datetime.now()
current_time = curr_time_raw.strftime("%Y-%m-%d %H:%M:%S")

st.title("InvestoInsight")
st.write("See Tomorrow's Profits Today 😵‍")

st_ticker = st.sidebar.text_input('Enter ticker: ', 'AAPL')
start_date = st.sidebar.text_input('Enter investment date: ', '01/09/2021')
end_date = st.sidebar.text_input('Enter potential divestment date: ', '01/03/2024')
objective = st.sidebar.selectbox("Select an objective", ["Expected Return", "Ideal Divestment Date"])

# # Load the pre-trained model
# model_path = '/Users/zoeyneo/code/zoeyneo/investoinsight/streamlit_app/model.py'  # Replace with the actual path to your model
# prediction_fig, intepretation_fig, mae_score, smape_score = load_pretrained_model(model_path)

### - RUN PROGRAM -
# Load the pre-trained model
loaded_model = load_pretrained_model()

# # Prepare your data based on the user's inputs (replace with your data preparation code)
# data = pd.DataFrame({'ticker': [st_ticker], 'start_date': [start_date], 'end_date': [end_date]})

# Make predictions using the loaded model
# prediction_fig, interpretation_fig, mae_score, smape_score = make_predictions(loaded_model)
res = make_predictions(loaded_model)
prediction_fig = res[0]
interpretation_fig = res[1]
mae_score = res[2]
smape_score = res[3]


if st.sidebar.button("Submit"):
    st.write(f"Results for {st_ticker} from {start_date} to {end_date}.")
    st.write(f"_last refreshed on {current_time}_")
    # st.write(f"📈📉 to insert charts here. random df below for fun")
    # st.write(f"Number of parameters in network: {tft_params}k")
    # st.write(f"suggested learning rate: {learning_rate}")
    st.write(f"MAE score: {mae_score}")
    st.write(f"SMAPE score: {smape_score}")
    st.plotly_chart(prediction_fig)
    st.plotly_chart(intepretation_fig)
    if objective == "Expected Return":
        st.write(f"to insert expected returns")
    if objective == "Ideal Divestment Date":
        st.write(f"to insert ideal end date")

    st.write(f"Latest News for {st_ticker} 📰")
    st.write("To Insert News Segment")


# # Tensorboard
# %load ext tensorboard
# %tensorboard --logdir "lightning_logs/version_98"
