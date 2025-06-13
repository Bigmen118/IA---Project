# Teclado Virtual por Gestos ✋⌨️

Un teclado virtual interactivo controlado por gestos de mano, desarrollado con Python, OpenCV y MediaPipe. Perfecto para entornos kioskos, pantallas táctiles o como herramienta de accesibilidad.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Este proyecto implementa un teclado virtual en tiempo real que se controla mediante gestos de la mano, utilizando una cámara web. El sistema detecta la posición del dedo índice para seleccionar teclas y un gesto de 'clic' (juntar el pulgar y el índice) para escribirlas.

---

## 🚀 Características

* **Control por Gestos:** No se necesita hardware adicional más allá de una cámara web.
* **Interfaz Completa:** Teclado QWERTY con números, letras, símbolos y teclas de función (Mayúsculas, Espacio, Borrar).
* **Cursor Visual:** Un círculo sigue la punta del dedo índice para que el usuario sepa dónde está "apuntando".
* **Feedback Interactivo:**
    * **Visual:** La tecla seleccionada se resalta en verde y se muestra una animación al hacer clic.
    * **Auditivo:** Se reproduce un sonido de "clic" cada vez que se presiona una tecla.
* **Área de Texto:** Un campo de texto en la parte superior muestra lo que se ha escrito en tiempo real.
* **Función de Mayúsculas (Caps Lock):** Permite alternar entre mayúsculas y minúsculas.
* **Anti-Rebote de Clics (Debouncing):** Evita que un solo gesto largo registre múltiples pulsaciones.

---

## 🛠️ Tecnologías Utilizadas

* **Python 3:** Lenguaje principal del proyecto.
* **OpenCV:** Para la captura de video de la cámara, el procesamiento de imágenes y el dibujo de la interfaz gráfica (teclado, texto, cursor).
* **MediaPipe:** Para la detección de manos y el seguimiento de sus puntos de referencia (landmarks) en tiempo real.
* **Pygame:** Utilizado específicamente por su módulo `mixer` para reproducir los efectos de sonido de las teclas con baja latencia.
* **NumPy:** Para operaciones numéricas, especialmente en la generación del sonido de respaldo.

---

## ⚙️ Instalación y Configuración

Sigue estos pasos para poner en marcha el proyecto en tu máquina local.

**1. Clona el Repositorio**
```bash
git clone [https://github.com/tu-usuario/teclado-virtual-gestos.git](https://github.com/tu-usuario/teclado-virtual-gestos.git)
cd teclado-virtual-gestos
```
*(Reemplaza `tu-usuario` con tu nombre de usuario de GitHub)*

**2. Crea y Activa un Entorno Virtual (Recomendado)**
* **Windows:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
* **macOS / Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

**3. Instala las Dependencias**
El proyecto utiliza un archivo `requirements.txt` para manejar las librerías necesarias.
```bash
pip install -r requirements.txt
```

---

## ▶️ Cómo Usarlo

Una vez que la instalación esté completa, simplemente ejecuta el script principal:
```bash
python main.py
```
* Asegúrate de que tu cámara web esté conectada y sin obstrucciones.
* Se abrirá una ventana mostrando la imagen de tu cámara y el teclado virtual.
* Mueve tu **dedo índice** para desplazar el cursor sobre las teclas.
* Junta la yema de tu **pulgar** con la de tu **dedo índice** para "hacer clic" y escribir la tecla seleccionada.
* Para salir de la aplicación, presiona la tecla `ESC`.

---

## 📄 Licencia

Este proyecto está distribuido bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
