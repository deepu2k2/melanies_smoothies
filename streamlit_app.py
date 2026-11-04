
# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.set_page_config(layout="centered")

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write(
    "Choose the fruits you want in your custom Smoothie!"
)

# Get customer name
name_on_order = st.text_input("Name on Smoothie:")

st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit options
my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

# Convert Snowpark DataFrame to Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Get fruit names for multiselect
fruit_options = pd_df["FRUIT_NAME"].tolist()

# Select ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# Convert list into string
ingredients_string = ""

if ingredients_list:
    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + " "

        # Get API search value from SEARCH_ON column
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write(
            "The search value for ",
            fruit_chosen,
            " is ",
            search_on,
            "."
        )

        # Display nutrition information
        st.subheader(fruit_chosen + " Nutrition Information")

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        sf_df = st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    st.write(ingredients_string)

# Submit order
if st.button("Submit Order"):

    if not name_on_order:
        st.warning("Please enter your name!")

    elif not ingredients_list:
        st.warning("Please select at least one ingredient!")

    else:
        my_insert_stmt = """
            INSERT INTO smoothies.public.orders
            (ingredients, name_on_order)
            VALUES (?, ?)
        """

        session.sql(
            my_insert_stmt,
            params=[ingredients_string.strip(), name_on_order]
        ).collect()

        st.success(
            "Your Smoothie is ordered!",
            icon="✅"
        )
