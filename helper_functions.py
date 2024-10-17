import pandas as pd

def processing_visits(df, catalog, brand):

    # Amazon dataframe
    amazon_df = pd.merge(df, catalog, left_on = 'SKU', right_on = 'SKU (AMAZON)', how = 'left')
    amazon_df = amazon_df[['Date', 'FAMILIA DE PRODUCTO', 'Sesiones - Total', 'Vistas de página - Total']]
    amazon_df.columns = ['Date', 'Product family', 'Sessions', 'Page views']

    # Remove commas
    amazon_df['Sessions'] = amazon_df['Sessions'].astype(str).str.replace(',', '').astype(int)
    amazon_df['Page views'] = amazon_df['Page views'].astype(str).str.replace(',', '').astype(int)

    # Total
    total_amazon_df = amazon_df.groupby('Date')[['Sessions', 'Page views']].sum()
    total_amazon_df['Product family'] = 'All ' + brand
    total_amazon_df = total_amazon_df.reset_index()

    # Group by date and family product
    amazon_df = amazon_df.groupby(['Date', 'Product family']).sum().reset_index()

    # Concat
    visits_df = pd.concat([amazon_df, total_amazon_df])

    # Pivot
    df_pivot = visits_df.pivot_table(index = 'Date', 
                          columns = 'Product family', 
                          values = ['Sessions', 'Page views'], 
                          aggfunc = 'sum')

    # Flatten the MultiIndex in the columns
    df_pivot.columns = [f'{col[1]} - {col[0]}' for col in df_pivot.columns]

    # Order the columns as 'Product A - Sessions', 'Product A - Page views'
    sorted_columns = []
    product_families = visits_df['Product family'].unique()

    for product in product_families:
        sorted_columns.append(f'{product} - Sessions')
        sorted_columns.append(f'{product} - Page views')

    # Reorder the columns
    df_pivot = df_pivot[sorted_columns]

    # Reset index to bring 'date' back as a column
    df_pivot = df_pivot.reset_index()
    df_pivot = df_pivot.fillna(0)

    return visits_df, df_pivot