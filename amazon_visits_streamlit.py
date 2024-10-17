import pandas as pd
import streamlit as st

from io import BytesIO
from helper_functions import *

st.title('Amazon - Sessions and Page Views')
st.header('File upload')
st.markdown('Upload file from Amazon Sellercentral to obtain Sessions and Page Views for each product/category.')

# Upload file
raw = st.file_uploader('Upload Amazon Sellercentral file', type = ['csv'])

if raw is not None:
    df = pd.read_csv(raw)
    st.success('File uploaded successfully.')

date = st.text_input('Insert date in the YYYY-MM-DD format, such as 2024-07-26.')
st.write('The date will be', date)
brand = st.selectbox('Select brand', ('InovaMX', 'Sognare'))
st.write('You selected', brand)

catalog_inova = pd.read_excel(r'https://raw.githubusercontent.com/francocibils/amazon_visits/main/amazon_catalog_inova.xlsx', engine = 'openpyxl')
catalog_sognare = pd.read_excel(r'https://raw.githubusercontent.com/francocibils/amazon_visits/main/amazon_catalog_sognare.xlsx', engine = 'openpyxl')

if st.button('Process file'):

    # Process dataframe
    df['Date'] = date
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.rename(columns = {'Sessions - Total': 'Sesiones - Total', 'Page Views - Total': 'Vistas de página - Total', '(Parent) ASIN': 'ASIN (parent)', 'Title': 'Titulo'})
    df = df.drop_duplicates(['ASIN (parent)', 'Date', 'Sesiones - Total'])

    # Catalog
    if brand == 'InovaMX':
        catalog = catalog_inova
    elif brand == 'Sognare':
        catalog = catalog_sognare

    catalog = catalog[['SKU (AMAZON)', 'FAMILIA DE PRODUCTO']]
    catalog['SKU (AMAZON)'] = catalog['SKU (AMAZON)'].astype(str)

    # Get processed file
    raw_visits, pivot_visits = processing_visits(df, catalog, brand)

    st.header('Processed data')
    st.success('Amazon files have been processed successfully.')
    
    # Convert the DataFrame to an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine = 'xlsxwriter') as writer:
        pivot_visits.to_excel(writer, index = False, sheet_name = 'Supermetrics table')
        raw_visits.to_excel(writer, index = False, sheet_name = 'Raw table')
        writer.close()

    # Rewind the buffer
    output.seek(0)

    # Create a download button
    st.download_button(
        label = "Download Excel file",
        data = output,
        file_name = f"Amazon - {brand} visits - {date}.xlsx",
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
