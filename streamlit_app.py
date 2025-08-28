# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Connect via Streamlit secrets
cnx = st.connection("snowflake")
session = cnx.session()

# --- LAB STEP: show FRUIT_NAME + SEARCH_ON and pause here ---
my_dataframe = (
    session.table("smoothies.public.fruit_options")
           .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

st.dataframe(data=my_dataframe, use_container_width=True)
st.stop()   # stop here so we can focus on verifying the dataframe

# ----------------- code below will not run yet -----------------

# Build options list from FRUIT_NAME (GUI uses friendly labels)
fruit_options = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

ingredients_string = ""

if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "
        st.subheader(fruit_chosen + " Nutrition Information")
        # NOTE: in a later step we will switch to SEARCH_ON for the API call
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + fruit_chosen
        )
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

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
