# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# -------------------------------- UI --------------------------------
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# --------------------------- Snowflake ------------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# Pull FRUIT_NAME + SEARCH_ON from FRUIT_OPTIONS
my_dataframe = (
    session.table("smoothies.public.fruit_options")
           .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

# Convert Snowpark DataFrame -> Pandas so we can use .loc
pd_df = my_dataframe.to_pandas()

# (Optional visual check — harmless to leave in)
st.dataframe(pd_df, use_container_width=True)

# ------------------------- Multiselect ------------------------------
# GUI shows friendly FRUIT_NAME values
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# -------------------- Show nutrition + build order ------------------
ingredients_string = ""

if ingredients_list:
    ingredients_string = ""
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Lookup the API-friendly value from SEARCH_ON
        search_on = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"].iloc[0]
        # st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')  # (debug line used in lab)

        st.subheader(f"{fruit_chosen} Nutrition Information")
        fruityvice_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

# -------------------------- Submit Order ----------------------------
time_to_insert = st.button("Submit Order")

if time_to_insert:
    if not name_on_order:
        st.warning("Please enter a name for the smoothie.")
    elif not ingredients_list:
        st.warning("Please choose at least one ingredient.")
    else:
        # Insert into ORDERS (ORDER_FILLED should default FALSE in your table)
        my_insert_stmt = (
            "insert into smoothies.public.orders(ingredients, name_on_order) "
            f"values ('{ingredients_string.strip()}','{name_on_order}')"
        )
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")
