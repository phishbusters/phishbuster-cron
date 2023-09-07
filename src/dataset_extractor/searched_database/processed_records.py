import pandas as pd

def read_last_processed(query):
    try:
        df = pd.read_csv("searched_database.csv")
    except FileNotFoundError:
        # Si el archivo no existe, crear un DataFrame vacío
        df = pd.DataFrame(columns=['SearchQuery', 'LastResultIndex', 'LastTweetIndex'])

    record = df[df['SearchQuery'] == query].iloc[0] if df[df['SearchQuery'] == query].shape[0] > 0 else None
    if record is not None:
        return record['LastResultIndex'], record['LastTweetIndex']
    else:
        return None, None


def update_last_processed(query, last_result_index, last_tweet_index):
    # Intentar leer el archivo CSV existente
    try:
        df = pd.read_csv("searched_database.csv")
    except FileNotFoundError:
        # Si el archivo no existe, crear un DataFrame vacío
        df = pd.DataFrame(columns=['SearchQuery', 'LastResultIndex', 'LastTweetIndex'])

    df['LastResultIndex'] = df['LastResultIndex'].astype(str)
    df['LastTweetIndex'] = df['LastTweetIndex'].astype(str)
    # Verificar si la consulta ya está en el DataFrame
    mask = df['SearchQuery'] == query

    profile_last_index  = last_result_index if last_result_index is not None else 0
    twitt_last_index = last_tweet_index if last_tweet_index is not None else 0
    if mask.sum() > 0:
        # Actualizar el registro existente
        if last_result_index is not None:
            df.loc[mask, 'LastResultIndex'] = profile_last_index
        if last_tweet_index is not None:
            df.loc[mask, 'LastTweetIndex'] = twitt_last_index
    else:
        # Agregar un nuevo registro
        new_row = {'SearchQuery': query, 'LastResultIndex': profile_last_index, 'LastTweetIndex': twitt_last_index}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Guardar el DataFrame actualizado
    df.to_csv("searched_database.csv", index=False)
