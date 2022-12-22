Lectura de firmas de documento Pagaré en PDF:

1. Convertir de base64 (pdf/jpg/png) a conjunto de imagenes en formato numpy array. Donde cada página corresponde a una imagen distinta
2. Tomar la 3ra hoja, la cual contiene la firma
3. Convertir imagen a escala de grises y convertir la imagen en blanco y negro, eliminando lo que no sea lo suficientemente oscuro
4. Separar la imagen por regiones continuas
5. Clasificar regiones por su tamaño y eliminar aquellas que son muy pequeñas o grandes
6. Tomar imagen luego de ser filtrada y ubicar las regiones continuas de interés nuevas
7. Tomar región más grande y retornarla

Lectura de firmas de documento CI en PDF/JPG/PNG (Este utiliza librería sign-detect la cual usa ImageMagick de fondo):

1. Convertir de base64 (pdf/jpg/png) a conjunto de imagenes en formato numpy array. Donde cada página corresponde a una imagen distinta
2. Tomar la 1ra hoja, la cual contiene usualmente la parte frontal de CI
3. Convertir imagen a escala de grises y convertir la imagen en blanco y negro, eliminando lo que no sea lo suficientemente oscuro
4. Separar la imagen por regiones continuas
5. Clasificar regiones por su tamaño y eliminar aquellas que son muy pequeñas o grandes
6. Tomar imagen luego de ser filtrada y ubicar las regiones continuas de interés nuevas
7. A todas las regiones que sean lo suficientemente grandes se les toman sus coordenadas
8. Tomar coordenadas de regiones de interés y calcular la región que las incluye a todas
9. Retornar imagen filtrada recortada de acuerdo a las coordenadas anteriores