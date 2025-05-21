# app-analisis-indices
app que despliega un analisis de medias moviles e indicadores
la misma busca los precios de los índices Nasdaq 100 - Dow Jones y un portfolio que se ingresa en el 
momento de la consulta.
luego despliega graficos con el datos de cruce dorado - asi de denomina al cruce de abajo hacia arriba
de la media móvil de 50 dias sobre la media móvil de 200 dias (con una ventana de 15 ruedas bursátiles),
eso es considerado una señal de compra según los analistas con un horizonte de mediano plazo. 
Además despliega una gráficos de RSI (14 periódos), para verificar la fuerza relativa 
también despliega un gráfico MACD (con periódos de 10 y 30 ruedas), con la misma lógica 
cuando la media de 10 corta de abajo hacia arriba a la media de 30 periódos sería considerar
una señal de compra para el corto plazo. 
Además sobre el tramo final de la app, se genera un test de rendimiento, punto de compra
el momento del cruce y hasta la fecha actual, mostrando el precio de compra y precios actual
y el rendimiento generado por la acción. 
Un tema no menor toda la información se puede descargar en formato excel. 
para poder ejecutar al app hay que escribir en la terminal streamlit run app.py o app_optional.py
