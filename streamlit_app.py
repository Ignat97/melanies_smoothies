# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Connect via Streamlit secrets
cnx = st.connection("snowflake")
session = cnx.session()  # <-- fix typo (snx -> cnx)

# Get fruit options and convert to a Python list of strings
fruits_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
fruit_options = [row["FRUIT_NAME"] for row in fruits_df.collect()]

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# Always define this (even if no selection)
ingredients_string = " ".join(ingredients_list) if ingredients_list else ""

# Build and run insert only when the user clicks
time_to_insert = st.button("Submit Order")

if time_to_insert:
    if not name_on_order:
        st.warning("Please enter a name for the smoothie.")
    elif not ingredients_list:
        st.warning("Please choose at least one ingredient.")
    else:
        my_insert_stmt = (
            "insert into smoothies.public.orders(ingredients, name_on_order) "
            f"values ('{ingredients_string}','{name_on_order}')"
        )
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")

# New section to display smoothieroot nutrition information
import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
# st.text(smoothiefroot_response.json())
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
