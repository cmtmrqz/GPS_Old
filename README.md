# GPSAfal
GPS system 

<h1>Preparacion De Raspberry Pi</h1>

<p>Habilitar Serial, SSH, VNC</p>
<pre>raspi-config</pre>

<p>Instalar libreria de Adafruit:</p>
<pre>pip install Adafruit_DHT</pre>

<p>Instalar librerias para utilizar bluetooth</p>
<pre>apt-get update</pre>
<pre>apt-get install bluetooth</pre>
<pre>apt-get install bluez</pre>
<pre>apt-get install python-bluez</pre>
<ul>
<li><p>Importante hacer pair entre dispositivos y trust (bluetoothctl)</p></li>
<li><p>Guardar <strong>rebootPiPy.sh </strong> en la Pi. Este archivo hace reboot a la Raspberry Pi si el codigo no esta corriendo. Ademas, es importante agregarlo en el crontab</p> <br> <pre>*/2 * * * * bash /path/rebootPiPy.sh<pre/></li>
 <li><p>Agregar archivo de python en crontab (reboot)</p><br><pre>@reboot python /path/nombreArchivo.py &</pre></li>
<li><p>Guardar <strong>btDiscoverable.sh </strong> en la Pi. Este archivo enciende el Bluetooth al iniciar la Raspbery Pi.</p></li>
<li><p>Agregar la siguiente linea de codigo a <i>/etc/rc.local/</i></p></li>
<pre>... <br> sudo path/btDiscoverable.sh <br> exit 0</pre>
</ul>

<h1>Archivos Version 1: </h1>
<ul>
<li><p><strong>camion.py:</strong> Este archivo almacena el numero del camion.</p></li>
<li><p><strong>fileManagement.py: </strong>Este archivo almacena las funcionas para leer y escribir archivos. Esto es importante para guardar los datos cuando se pierda conexion a internet</p></li>
<li><p><strong>gpsBtPost.py: </strong> Este archivo realiza el post de gps y temperaturas al WEB API. Los datos de temperaturas se reciben por bluetooth.</p></li>
<li><p><strong>gpsPost.py: </strong> Este archivo hace post solo de gps al WEB API.</p></li>
<li><p><strong>isConnected.py: </strong> Este archivo contiene la funcion que detecta si tenemos conexion a internet para realizar el post. Este archivo solo fue de prueba, no es importado por ningun otro archivo</p></li>
<li><p><strong>justTemps.py: </strong> Este archivo realiza las lecturas de temperaturas y las envia por bluetooth para que otro dispositivo con conexion a internet realice el post al WEB API</p></li>
<li><p><strong>main.py: </strong> Este archivo realiza el post de gps y temperaturas al WEB API. A diferencia de gpsBtPost, este archivo adquiere ambos datos, es decir, todo esta conectado a esta pi, los sensores de temperaturas y el HAT</p></li>
<li><p><strong>reSend.py: </strong> Este fue un archivo para probar la funcion de reenviar los datos almacenados cuando no habia conexion. Este archivo no es importado por ningun otro.</p></li>
<li><p><strong>response.json: </strong> Este archivo muestra un ejemplo de los datos que se deben enviar al WEB API.</p></li>
<li><p><strong>tempsPost.py: </strong> Este archivo realiza un post solo de temperaturas al WEB API.</p></li>
<li><p><strong>temps.py: </strong> Este archivo contiene la funcion para leer las temperaturas. Este arvhivo es importado por justTemps, tempsPost, main.</p></li>
<li><p><strong>turnOn.py: </strong> Este archivo contiene el script para enceder el HAT.</p></li>
</ul>

<h1>Archivos Version 2: </h1>
<ul>
<li><p><strong>camion.py:</strong> Este archivo almacena el numero del camion.</p></li>
<li><p><strong>clases.py: </strong> Este archivo contiene la clase guardian t captainTemps, que se utilizan para leer GPS,temperaturas, asignar IP, hacer post.</p></li>
<li><p><strong>fileManagement.py: </strong>Este archivo almacena las funcionas para leer y escribir archivos. Esto es importante para guardar los datos cuando se pierda conexion a internet</p></li>
<li><p><strong>gpsBtPost.py: </strong> Este archivo realiza el post de gps y temperaturas al WEB API. Los datos de temperaturas se reciben por bluetooth desde otra Raspberry Pi.</p></li>
<li><p><strong>gpsPost.py: </strong> Este archivo hace post solo de gps al WEB API.</p></li>
<li><p><strong>isConnected.py: </strong> Este archivo contiene la funcion que detecta si tenemos conexion a internet para realizar el post. Este archivo solo fue de prueba, no es importado por ningun otro archivo</p></li>
<li><p><strong>justTemps.py: </strong> Este archivo realiza las lecturas de temperaturas y las envia por bluetooth para que otro dispositivo con conexion a internet realice el post al WEB API</p></li>
<li><p><strong>main.py: </strong> Este archivo realiza el post de gps y temperaturas al WEB API. A diferencia de gpsBtPost, este archivo adquiere ambos datos, es decir, todo esta conectado a esta pi, los sensores de temperaturas y el HAT</p></li>
<li><p><strong>tempsPost.py: </strong> Este archivo realiza un post solo de temperaturas al WEB API.</p></li>
<li><p><strong>temps.py: </strong> Este archivo contiene la funcion para leer las temperaturas. Este arvhivo es importado por justTemps, tempsPost, main.</p></li>
<li><p><strong>turnOn.py: </strong> Este archivo contiene el script para enceder el HAT.</p></li>
</ul>

<h1>Archivos Version 3: </h1>
<ul>
<li><p><strong>camion.py:</strong> Este archivo almacena el numero del camion.</p></li>
<li><p><strong>clases.py: </strong> Este archivo contiene la clase guardian t captainTemps, que se utilizan para leer GPS,temperaturas, asignar IP, hacer post.</p></li>
<li><p><strong>fileManagement.py: </strong>Este archivo almacena las funcionas para leer y escribir archivos. Esto es importante para guardar los datos cuando se pierda conexion a internet</p></li>
<li><p><strong>gpsBtPost.py: </strong> Este archivo realiza el post de gps y temperaturas al WEB API. Los datos de temperaturas se reciben por bluetooth desde un Arduino.</p></li>
<li><p><strong>gpsPost.py: </strong> Este archivo hace post solo de gps al WEB API.</p></li>
<li><p><strong>isConnected.py: </strong> Este archivo contiene la funcion que detecta si tenemos conexion a internet para realizar el post. Este archivo solo fue de prueba, no es importado por ningun otro archivo</p></li>
<li><p><strong>justTemps.py: </strong> Este archivo realiza las lecturas de temperaturas y las envia por bluetooth para que otro dispositivo con conexion a internet realice el post al WEB API</p></li>
<li><p><strong>main.py: </strong> Este archivo realiza el post de gps y temperaturas al WEB API. A diferencia de gpsBtPost, este archivo adquiere ambos datos, es decir, todo esta conectado a esta pi, los sensores de temperaturas y el HAT</p></li>
<li><p><strong>tempsPost.py: </strong> Este archivo realiza un post solo de temperaturas al WEB API.</p></li>
<li><p><strong>temps.py: </strong> Este archivo contiene la funcion para leer las temperaturas. Este arvhivo es importado por justTemps, tempsPost, main.</p></li>
<li><p><strong>turnOn.py: </strong> Este archivo contiene el script para enceder el HAT.</p></li>
</ul>

<h1>Archivos Version 4: </h1>
<ul>
<li><p><strong>camion.py:</strong> Este archivo almacena el numero del camion.</p></li>
<li><p><strong>clases.py: </strong> Este archivo contiene la clase guardian t captainTemps, que se utilizan para leer GPS,temperaturas, asignar IP, hacer post.</p></li>
<li><p><strong>fileManagement.py: </strong>Este archivo almacena las funcionas para leer y escribir archivos. Esto es importante para guardar los datos cuando se pierda conexion a internet</p></li>
<li><p><strong>gpsBtPost.py: </strong> Este archivo realiza el post de gps y temperaturas al WEB API. Los datos de temperaturas se reciben por bluetooth desde un Arduino. Esta nueva version tiene una nueva fucionalidad: el tiempo "muerto" para obtener datos de GPS es utilizado para realizar el envio de los datos que estan en el log, de esta manera se asegura que los daros de GPS se recopilen aproximadamente cada 2 minutos</p></li>
<li><p><strong>isConnected.py: </strong> Este archivo contiene la funcion que detecta si tenemos conexion a internet para realizar el post. Este archivo solo fue de prueba, no es importado por ningun otro archivo</p></li>
<li><p><strong>temps.py: </strong> Este archivo contiene la funcion para leer las temperaturas. Este arvhivo es importado por justTemps, tempsPost, main.</p></li>
<li><p><strong>turnOn.py: </strong> Este archivo contiene el script para enceder el HAT.</p></li>
</ul>

<h1>Archivos Version 5: </h1>
<ul>
<li><p><strong>camion.py:</strong> Este archivo almacena el numero del camion.</p></li>
<li><p><strong>clases.py: </strong> Este archivo contiene la clase guardian t captainTemps, que se utilizan para leer GPS,temperaturas, asignar IP, hacer post.</p></li>
<li><p><strong>fileManagement.py: </strong>Este archivo almacena las funcionas para leer y escribir archivos. Esto es importante para guardar los datos cuando se pierda conexion a internet</p></li>
<li><p><strong>gpsBtPost.py: </strong> Este archivo realiza el post de gps y temperaturas al WEB API. Los datos de temperaturas se reciben por bluetooth desde un Arduino. Se modifico la funcionalidad de la version 4, para que tambien envie los datos de temperauras en el tiempo "muerto" si no hay logs. </p></li>
<li><p><strong>isConnected.py: </strong> Este archivo contiene la funcion que detecta si tenemos conexion a internet para realizar el post. Este archivo solo fue de prueba, no es importado por ningun otro archivo</p></li>
<li><p><strong>temps.py: </strong> Este archivo contiene la funcion para leer las temperaturas. Este arvhivo es importado por justTemps, tempsPost, main.</p></li>
<li><p><strong>turnOn.py: </strong> Este archivo contiene el script para enceder el HAT.</p></li>
</ul>

<h1>Archivos Version 6: </h1>
<ul>
<li><p><strong>camion.py:</strong> Este archivo almacena el numero del camion.</p></li>
<li><p><strong>clases.py: </strong> Este archivo contiene la clase guardian t captainTemps, que se utilizan para leer GPS,temperaturas, asignar IP, hacer post.</p></li>
<li><p><strong>fileManagement.py: </strong>Este archivo almacena las funcionas para leer y escribir archivos. Esto es importante para guardar los datos cuando se pierda conexion a internet</p></li>
<li><p><strong>gpsBtPost.py: </strong> Este archivo realiza el post de gps y temperaturas al WEB API. Los datos de temperaturas se reciben por bluetooth desde un Arduino. Se agrego una funcionalidad para intentar la perdida de datos de GPS. La funcionalidad consiste en tomar la posicion de GSM si el fix del GPS se ha perdido </p></li>
<li><p><strong>isConnected.py: </strong> Este archivo contiene la funcion que detecta si tenemos conexion a internet para realizar el post. Este archivo solo fue de prueba, no es importado por ningun otro archivo</p></li>
<li><p><strong>temps.py: </strong> Este archivo contiene la funcion para leer las temperaturas. Este arvhivo es importado por justTemps, tempsPost, main.</p></li>
<li><p><strong>turnOn.py: </strong> Este archivo contiene el script para enceder el HAT.</p></li>
</ul>

