# 🧠 Carrera de Mente

**El clásico juego de trivia para toda la familia — ArgOS Platinum Edition**

[![Version](https://img.shields.io/badge/versión-1.0.0-blue)](https://github.com/Tavo78ok)
[![Platform](https://img.shields.io/badge/plataforma-Linux-orange)](https://github.com/Tavo78ok)
[![GTK](https://img.shields.io/badge/GTK-4.0%20%2F%20libadwaita-green)](https://gtk.org)
[![License](https://img.shields.io/badge/licencia-MIT-lightgrey)](LICENSE)

---

## 📖 Descripción

Carrera de Mente es un juego de trivia para **1 a 4 jugadores** inspirado en el clásico juego de mesa. Cada jugador debe responder preguntas de **6 categorías** distintas para coleccionar sus fichas. El primero en completar las 6 gana la partida.

Las preguntas provienen de un banco integrado y, opcionalmente, son generadas en tiempo real por **Inteligencia Artificial** (Claude de Anthropic).

---

## ✨ Características

- 🎮 **1 a 4 jugadores** en el mismo equipo
- 🗂️ **6 categorías** con colores únicos:
  | Categoría | Color |
  |---|---|
  | 🧠 Cultura General | Azul |
  | 🎬 Entretenimiento | Púrpura |
  | 🔬 Ciencia y Tecnología | Verde |
  | 📜 Historia | Naranja |
  | 🌍 Geografía | Teal |
  | ⚽ Deportes | Rojo |
- 🤖 **Preguntas generadas por IA** (40% del tiempo si la API key está configurada)
- 📚 **Banco de preguntas integrado** — funciona 100% sin internet
- 🔄 Sin repetición de preguntas hasta agotar el banco
- 🎨 Interfaz moderna con **GTK4 + libadwaita** siguiendo GNOME HIG
- 🏆 Pantalla de ganador con fichas de categorías

---

## 📦 Instalación

### Desde el paquete .deb (recomendado)

```bash
sudo dpkg -i carrera-mente_1.0.0_all.deb
sudo apt-get install -f
```

### Dependencias manuales

```bash
sudo apt install python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 python3-pip
```

### Dependencia de IA (opcional)

```bash
pip3 install anthropic --break-system-packages
```

---

## 🚀 Uso

```bash
# Sin IA
carrera-mente

# Con preguntas generadas por IA
ANTHROPIC_API_KEY="sk-ant-..." carrera-mente
```

Para configurar la API key de forma permanente:

```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc
source ~/.bashrc
```

Obtén tu API key en [console.anthropic.com](https://console.anthropic.com).

---

## 🕹️ Cómo jugar

1. **Configura la partida** — elige número de jugadores (1-4) y sus nombres.
2. **Elige una categoría** — el jugador activo selecciona una de las 6 categorías.
3. **Responde la pregunta** — tienes 4 opciones (A, B, C, D).
4. **Gana una ficha** — si acertás, esa categoría queda marcada.
5. **Turno siguiente** — pasa al próximo jugador.
6. **¡Victoria!** — el primero en completar las **6 fichas** gana.

---

## 🤖 Integración con IA

Cuando `ANTHROPIC_API_KEY` está configurada y la librería `anthropic` está instalada, el juego genera preguntas nuevas mediante el modelo **Claude Sonnet** de Anthropic con una probabilidad del 40% por turno. Las preguntas siempre son en español de América Latina y están adaptadas a la categoría seleccionada.

Si la generación falla por cualquier motivo (sin conexión, cuota agotada, etc.), el juego recurre automáticamente al banco local sin interrumpir la partida.

Las preguntas generadas por IA se identifican con el badge **✨ Pregunta generada por IA**.

---

## 🗂️ Estructura del paquete

```
/usr/bin/carrera-mente                                  ← Ejecutable
/usr/lib/carrera-mente/carrera_mente.py                 ← App principal
/usr/share/applications/io.openargos.carrera-mente.desktop
/usr/share/icons/hicolor/scalable/apps/io.openargos.carrera-mente.svg
/usr/share/doc/carrera-mente/copyright
```

---

## 🛠️ Desarrollo

### Ejecutar desde fuente

```bash
git clone https://github.com/Tavo78ok/carrera-mente
cd carrera-mente
python3 carrera_mente.py
```

### Stack tecnológico

- **Python 3.10+**
- **GTK4 + libadwaita** — UI moderna con soporte para temas GNOME
- **anthropic** — cliente oficial para la API de Claude
- **threading + GLib.idle_add** — generación de preguntas sin bloquear la interfaz

### Construir el .deb

```bash
dpkg-deb --build --root-owner-group carrera-mente_1.0.0/ carrera-mente_1.0.0_all.deb
```

---

## 🐛 Problemas conocidos

- La generación por IA requiere conexión a internet y una API key válida de Anthropic.
- En distribuciones sin `libadwaita` >= 1.2, la app puede no iniciar. Asegurate de tener `gir1.2-adw-1` instalado.

---

## 📄 Licencia

MIT © 2026 [Andrés (Tavo78ok)](https://github.com/Tavo78ok)

---

## 🏗️ Parte de ArgOS Platinum Edition

> Carrera de Mente es parte del ecosistema de aplicaciones nativas de **ArgOS Platinum Edition**, una distribución Linux basada en Debian con aplicaciones propias desarrolladas en Python + GTK4/libadwaita.


