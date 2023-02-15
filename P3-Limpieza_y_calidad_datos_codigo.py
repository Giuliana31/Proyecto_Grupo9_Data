import pandas as pd
import numpy as np

airbnbmadrid = pd.read_csv('airbnb-listings.csv', encoding = 'utf-8-sig', sep = ";")

#Vemos su forma
print(airbnbmadrid.shape)

#Exploramos las columnas para ver cuáles nos interesan
print(airbnbmadrid.columns.values)

#Hacemos una primera selección con las columnas que queremos
airbnbmadrid_selected = airbnbmadrid[['ID', 'Name', 'Listing Url', 'Host ID', 'Neighbourhood Group Cleansed', 'City', 'State', 'Zipcode', 'Country Code', 'Country', 'Latitude', 'Longitude', 'Property Type', 'Room Type', 'Square Feet', 'Price', 'Weekly Price', 'Monthly Price', 'Security Deposit', 'Cleaning Fee', 'Number of Reviews', 'Review Scores Rating', 'Review Scores Accuracy', 'Review Scores Cleanliness', 'Review Scores Checkin', 'Review Scores Communication', 'Review Scores Location', 'Review Scores Value', 'Cancellation Policy', 'Accommodates', 'Bathrooms', 'Bedrooms', 'Beds', 'Host ID', 'Host URL', 'Host Name', 'Host Since', 'Host Location', 'Host About', 'Host Response Time', 'Host Response Rate', 'Host Acceptance Rate', 'Host Thumbnail Url', 'Host Picture Url', 'Host Neighbourhood', 'Host Listings Count', 'Host Total Listings Count', 'Host Verifications']]

#Inspeccionamos la cantidad de NA que hay en cada una y tomar decisiones sobre qué eliminar
print(airbnbmadrid_selected.isna().sum())

#Eliminamos las filas que no tienen precio, los Host sin nombre, y la fila que no tiene codigo de país, ya que al buscarla vemos que es de Italia
airbnbmadrid_selected = airbnbmadrid_selected[airbnbmadrid_selected['Price'].notna()]
airbnbmadrid_selected = airbnbmadrid_selected[airbnbmadrid_selected['Host Name'].notna()]
airbnbmadrid_selected = airbnbmadrid_selected[airbnbmadrid_selected['Country'].notna()]

#Eliminamos la columna de Square Feet porque tiene demasiados valores NA
airbnbmadrid_selected.drop(columns = ['Square Feet', 'Host Location', 'Host About', 'Host Response Time', 'Host Response Rate', 'Host Acceptance Rate', 'Host Thumbnail Url', 'Host Picture Url', 'Host Neighbourhood', 'Host Listings Count', 'Host Total Listings Count'], inplace = True)

# Después de haber eliminado filas, reseteamos el índice 
airbnbmadrid_selected.reset_index(drop=True)

#Observando algunas columnas más en detalle, vemos que la columna 'Country Code' tiene valores que son fuera de España, así que nos deshacemos de esas filas
airbnbmadrid_selected = airbnbmadrid_selected[airbnbmadrid_selected['Country Code']== 'ES']

# También la columna 'State' tiene valores diferentes a Madrid. Así como formas diferentes de referirse a Madrid, por lo que hacemos un filtrado de esa columna por la palabra 'Madrid', y la palabra '马德里' que en chino también significa Madrid, y que hemos observado que existe en nuestro dataset
airbnbmadrid_selected = airbnbmadrid_selected[airbnbmadrid_selected.stack().str.contains('|'.join(['Madrid','马德里'])).any(level=0)]

#Rellenamos los NA de 'Security Deposit' y 'Cleaning Fee' con 0, porque si es NA es que está incluido en el precio
airbnbmadrid_selected.loc[:, ('Security Deposit', 'Cleaning Fee')] = airbnbmadrid_selected.loc[:, ('Security Deposit', 'Cleaning Fee')].fillna(0)

#Creamos una nueva columna con la suma de los valores del Security Deposit y Cleaning Fee, para poder tener los Extras que se le añade al precio

airbnbmadrid_selected['Extras'] = airbnbmadrid_selected['Cleaning Fee'] + airbnbmadrid_selected['Security Deposit']

#Cambiamos el dato de la columna de 'Host Verifications' por Yes, es un host veríficado, y No, no lo es. Lo hacemos en base a los NA.
airbnbmadrid_selected.loc[:, 'Host Verifications'] = airbnbmadrid_selected['Host Verifications'].isna()
airbnbmadrid_selected.loc[:,'Host Verifications'] = ['No' if val else 'Yes' for val in airbnbmadrid_selected['Host Verifications']]

# Creamos un bucle for para crear una nueva columna en la que sustituyamos los valores NaN de la columna Weekly Price, por los valores de la columna Weekly Price Calculated, pero manteniendo los valores originales de las viviendas que si proporcionan ese dato.

def price_new(df, column1, column2):
    wpn = []
    for ind, valor in df[column1].iteritems():
        if pd.notnull(valor):
            wpn.append(valor)
        else:
            wpn.append(df.loc[ind, column2])
    return wpn

#Creamos una nueva columna con los Precios semanales calculados en base al precio por dia
airbnbmadrid_selected['Weekly Price Calculated'] = airbnbmadrid_selected.loc[:,'Price']*7
airbnbmadrid_selected['Weekly Price New'] = price_new(airbnbmadrid_selected, 'Weekly Price', 'Weekly Price Calculated')

#Repetimos el proceso para los precios mensuales
airbnbmadrid_selected['Monthly Price Calculated'] = airbnbmadrid_selected.loc[:,'Price']*30
airbnbmadrid_selected['Monthly Price New'] = price_new(airbnbmadrid_selected, 'Monthly Price', 'Monthly Price Calculated')

# Creamos dos columnas nuevas para diferenciar entre los precios semanales y mensuales puestos por el dueño, y los calculados por nosotras.
    #Meses
airbnbmadrid_selected['Monthly Price Discounted'] = airbnbmadrid_selected['Monthly Price'].notna()
airbnbmadrid_selected.loc[:,'Monthly Price Discounted'] = ['With Discount' if val else 'Without Discount' for val in airbnbmadrid_selected['Monthly Price Discounted']]
    #Semanas
airbnbmadrid_selected['Weekly Price Discounted'] = airbnbmadrid_selected['Weekly Price'].notna()
airbnbmadrid_selected.loc[:,'Weekly Price Discounted'] = ['With Discount' if val else 'Without Discount' for val in airbnbmadrid_selected['Weekly Price Discounted']]

#Para las columnas de Reviews, a los valores NA le asignamos el valor 0, el cual es menor a la mínima puntuación que se puede recibir, por lo que es claramente identificable.
airbnbmadrid_selected.loc[:,['Review Scores Rating', 'Review Scores Accuracy','Review Scores Cleanliness', 'Review Scores Checkin', 'Review Scores Communication', 'Review Scores Location', 'Review Scores Value']] = airbnbmadrid_selected.loc[:,['Review Scores Rating', 'Review Scores Accuracy', 'Review Scores Cleanliness', 'Review Scores Checkin', 'Review Scores Communication', 'Review Scores Location', 'Review Scores Value']].fillna(0)

#Creamos una nueva columna que sea la media de las reviews que nos interesan.

airbnbmadrid_selected['Reviews Mean']= airbnbmadrid_selected[['Review Scores Cleanliness', 'Review Scores Checkin', 'Review Scores Communication', 'Review Scores Location', 'Review Scores Value']].mean(axis=1)

#Finalmente nuestro recuento de NA queda así
print(airbnbmadrid_selected.isna().sum())

#Vemos el boxplot en R y decidimos hacer una limpieza de outliers de Price, de solo ciertos valores de la columna Property Type. Primero creamos la funcion con la que obtendremos la mascara de booleanos que necesitamos para el filtrado. Es una mascara que calcula el espacio intercuartil superior, y marca como False los valores que estan en este intervalo.

def iqr_calculation(df, columncomp):
    airbnb_q = df[columncomp].quantile(np.arange(0.25, 1, 0.25))
    q1, q3 = np.percentile(df[columncomp], [25,75])
    iqr = q3 - q1
    airbnbmadrid_mask = df[columncomp] > (airbnb_q.iloc[2] + 1.5*iqr)
    return airbnbmadrid_mask

#VILLA
airbnbmadrid_villa = airbnbmadrid_selected[airbnbmadrid_selected['Property Type'] == 'Villa']

#OTHER
airbnbmadrid_other = airbnbmadrid_selected[airbnbmadrid_selected['Property Type'] == 'Other']

#LOFT
airbnbmadrid_loft = airbnbmadrid_selected[airbnbmadrid_selected['Property Type'] == 'Loft']

#HOUSE
airbnbmadrid_house = airbnbmadrid_selected[airbnbmadrid_selected['Property Type'] == 'House']

#DORM
airbnbmadrid_dorm = airbnbmadrid_selected[airbnbmadrid_selected['Property Type'] == 'Dorm']

#Condominium
airbnbmadrid_condominium = airbnbmadrid_selected[airbnbmadrid_selected['Property Type'] == 'Condominium']

#CHALET
airbnbmadrid_chalet = airbnbmadrid_selected[airbnbmadrid_selected['Property Type'] == 'Chalet']

#BED & BREAKFAST
airbnbmadrid_bnb = airbnbmadrid_selected[airbnbmadrid_selected['Property Type'] == 'Bed & Breakfast']

#APARTMENT
airbnbmadrid_apartment = airbnbmadrid_selected[airbnbmadrid_selected['Property Type'] == 'Apartment']

#BOUTIQUE HOTEL
airbnbmadrid_bh = airbnbmadrid_selected[airbnbmadrid_selected['Property Type'] == 'Boutique hotel']

new_airbnbmadrid = airbnbmadrid_selected[((airbnbmadrid_selected['Property Type'] == 'Apartment') & (iqr_calculation(airbnbmadrid_apartment, 'Price') == False))| ((airbnbmadrid_selected['Property Type'] == 'Bed & Breakfast') & (iqr_calculation(airbnbmadrid_bnb,'Price') == False)) | ((airbnbmadrid_selected['Property Type'] == 'Chalet') & (iqr_calculation(airbnbmadrid_chalet, 'Price') == False)) | ((airbnbmadrid_selected['Property Type'] == 'Condominium') & (iqr_calculation(airbnbmadrid_condominium, 'Price') == False)) | ((airbnbmadrid_selected['Property Type'] == 'Dorm') & (iqr_calculation(airbnbmadrid_dorm, 'Price') == False)) | ((airbnbmadrid_selected['Property Type'] == 'House') & (iqr_calculation(airbnbmadrid_house, 'Price') == False)) | ((airbnbmadrid_selected['Property Type'] == 'Loft') & (iqr_calculation(airbnbmadrid_loft, 'Price') == False)) | ((airbnbmadrid_selected['Property Type'] == 'Boutique hotel') & (iqr_calculation(airbnbmadrid_bh, 'Price') == False)) | ((airbnbmadrid_selected['Property Type'] == 'Other') & (iqr_calculation(airbnbmadrid_other, 'Price') == False)) | ((airbnbmadrid_selected['Property Type'] == 'Villa') & (iqr_calculation(airbnbmadrid_villa, 'Price') == False)) | (airbnbmadrid_selected['Property Type'] == 'Hostel') | (airbnbmadrid_selected['Property Type'] == 'Guesthouse') | (airbnbmadrid_selected['Property Type'] =='Serviced apartment') | (airbnbmadrid_selected['Property Type'] == 'Guest suite')| (airbnbmadrid_selected['Property Type'] == 'Townhouse') | (airbnbmadrid_selected['Property Type'] =='Casa particular') | (airbnbmadrid_selected['Property Type'] =='Tent') | (airbnbmadrid_selected['Property Type'] =='Boat') | (airbnbmadrid_selected['Property Type'] == 'Earth House') | (airbnbmadrid_selected['Property Type'] == 'Bungalow') | (airbnbmadrid_selected['Property Type'] =='Camper/RV') | (airbnbmadrid_selected['Property Type'] =='Timeshare')]

#Tras esto observamos los boxplot de Weekly Price y Monthly Price. El Weekly Price no tiene grandes outliers, por lo que lo dejamos. Sin embargo, el Montly Price tiene un dato que se aleja mucho de la media, por lo que lo limpiamos.
new_airbnbmadrid['Monthly Price New'] = new_airbnbmadrid.loc[(iqr_calculation(new_airbnbmadrid,'Monthly Price')) == False]['Monthly Price New']



new_airbnbmadrid.to_excel('airbnbmadrid_selected_excelfinal_v1.xlsx', index = False)












