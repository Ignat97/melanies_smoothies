# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# ---------------- UI header ----------------
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# ---------------- Snowflake connection ----------------
cnx = st.connection("snowflake")
session = cnx.session()

# ---------------- LAB STEP: bring in SEARCH_ON and convert to pandas ----------------
# Pull FRUIT_NAME + SEARCH_ON from FRUIT_OPTIONS
my_dataframe = (
    session.table("smoothies.public.fruit_options")
           .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

# Convert Snowpark DF -> pandas DF so we can use .loc later
pd_df = my_dataframe.to_pandas()

# Show it so we can verify what’s feeding the multiselect
st.dataframe(pd_df, use_container_width=True)

# Per the lab, pause here to verify. The rest of the app is below.
st.stop()

# ==============================
# code below won’t run until you remove st.stop() above
# ==============================

# Build the multiselect options from the friendly names
fruit_options = pd_df["FRUIT_NAME"].tolist()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# Always define this (even if no selection)
ingredients_string = ""

if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Look up the API-friendly value from SEARCH_ON
        match = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"]
        search_on = match.iloc[0] if not match.empty else fruit_chosen

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Call the API using the SEARCH_ON value
        # (exact string per lab; no slugging unless later instructed)
        resp = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        st.dataframe(data=resp.json(), use_container_width=True)

# Submit order -> insert into ORDERS
time_to_insert = st.button("Submit Order")

if time_to_insert:
    if not name_on_order:
        st.warning("Please enter a name for the smoothie.")
    elif not ingredients_list:
        st.warning("Please choose at least one ingredient.")
    else:
        my_insert_stmt = (
            "insert into smoothies.public.orders(ingredients, name_on_order) "
            f"values ('{ingredients_string.strip()}','{name_on_order}')"
        )
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")
