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

# ---------------- Pull fruit options ----------------
my_dataframe = (
    session.table("smoothies.public.fruit_options")
           .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

# Convert Snowpark DF -> pandas DF
pd_df = my_dataframe.to_pandas()

# Show both FRUIT_NAME + SEARCH_ON so we can confirm mapping
st.dataframe(pd_df, use_container_width=True)

# ---------------- Multiselect ----------------
fruit_options = pd_df["FRUIT_NAME"].tolist()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# ---------------- Build smoothie ----------------
ingredients_string = ""

if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Look up the SEARCH_ON value for the chosen fruit
        search_on = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"].iloc[0]

        # Show what’s happening (lab requirement)
        st.write("The search value for", fruit_chosen, "is", search_on, ".")

        # Show nutrition info using SEARCH_ON in the API call
        st.subheader(fruit_chosen + " Nutrition Information")
        fruityvice_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )
        st.dataframe(data=fruityvice_response.json(), use_container_width=True)

# ---------------- Submit order ----------------
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
