from spotipy.oauth2 import SpotifyClientCredentials
from mutagen.id3 import ID3, APIC, TPE1, TALB, TYER
from youtubesearchpython import VideosSearch
from mutagen.mp4 import MP4, MP4Cover
from pydub import AudioSegment
from platform import system
from pytube import Playlist
from pytube import YouTube
from time import sleep
from art import *
import requests
import zipfile
import spotipy
import shutil
import json
import os


# ------------------------------ #


# Variables de éxito y error para ser mostradas al final del programa.
audios_exito = 0
audios_error = 0

videos_exito = 0
videos_error = 0


# ------------------------------ #


# Función para eliminar la consola dependiendo del sistema operativo.
def limpiar_pantalla():
    if system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


# ------------------------------ #


# Crear el archivo de configuración si es que no existe.
try:
    # Verificar si existe el archivo de configuración
    with open("config.json", "r") as f:
        config = json.load(f)

    client_id = config["Client_ID"]
    client_secret = config["Secret_ID"]

except:
    # Si no existe, crearlo con la configuración por defecto y salir del programa para que el usuario lo configure
    config = {
        "Client_ID": "",
        "Secret_ID": "",
        "Directorio": "/",
        "Calidad_audio_video": "avg",  # Disponible max (máxima calidad), min (mínima calidad), avg (calidad promedio)
        "Descargar_video": False,
        "Descargar_audio": True,
        "Busqueda_en_YouTube": True,
        "Utilizar_playlist_YouTube": False,
        "Utilizar_playlist_Spotify": False,
        "Utilizar_link_de_YouTube": False,
        "Utilizar_link_de_Spotify": False,
        "Utilizar_canciones.txt": False,
        "Eliminar_canciones.txt_automaticamente": False,
        "Scrappear_metadata_Spotify": True,
        "Convertir_a_zip": False,
    }
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    limpiar_pantalla()
    tprint("YouTube - Downloader")
    print("Developed by Fvitu")
    print(
        "------------------------------------------------------------------------------------------\n"
    )
    sleep(2)
    limpiar_pantalla()

    print(
        "Bienvenido a esta aplicación creada por Fvitu, aquí podrá descargar videos o audios de YouTube totalmente gratis y de manera sencilla. Solo tendrá que configurar el archivo llamado 'config.json' para poder utilizar esta aplicación. Gracias"
    )


# ------------------------------ #


# Crear el archivo necesario para descargar canciones a través de este archivo de texto. Si el usuario no lo necesita y el archivo existe, entonces se elimina automáticamente.
if config["Utilizar_canciones.txt"]:
    if not os.path.exists("canciones.txt"):
        with open("canciones.txt", "w") as f:
            f.write("")
else:
    if os.path.exists("canciones.txt"):
        os.remove("canciones.txt")


# ------------------------------ #


# Función para crear carpetas determinadas si es que no existen.
def crear_carpeta(carpeta):
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)


# ------------------------------ #


# Función para mover archivos a una carpeta específica.
def mover_archivo(cancion, carpeta):
    mp4_path = os.path.join(carpeta, cancion)
    shutil.move(cancion, mp4_path)


# ------------------------------ #


# Función para verificar si el archivo ya existe.
def archivo_duplicado(directorio, tipo, nombre):
    try:
        carpeta_tipo = tipo.capitalize()  # Convertir a mayúscula la primera letra
        directorio = os.path.join(directorio, carpeta_tipo)
        archivos_en_ruta_actual = os.listdir(directorio)
        return nombre in archivos_en_ruta_actual
    except Exception as e:
        print(f"❌ Ocurrió un error al comprobar si el archivo es duplicado: {e}")
        return False


# ------------------------------ #


# Función para obtener el nombre del artista de YouTube.
def obtener_artista_youtube(url):
    try:
        yt = YouTube(url)
        return yt.author if yt.author else ""
    except Exception as e:
        print(f"❌ Ocurrió un error al obtener el nombre del artista de YouTube: {e}")
        return ""


# ------------------------------ #


# Función para obtener los nombres de los artistas como una cadena separada por comas.
def obtener_nombre_artistas(track):
    if track["artists"]:
        artists = [artist["name"] for artist in track["artists"]]
        return ", ".join(artists)
    return ""


# ------------------------------ #


# Función para obtener el nombre del álbum completo desde la API de Spotify.
def obtener_nombre_album(sp, album_id):
    try:
        album = sp.album(album_id)
        if "name" in album:
            return album["name"]
        return None
    except Exception as e:
        print(f"❌ Ocurrió un error al obtener el nombre del álbum: {e}")
        return None


# ------------------------------ #


# Función para descargar la portada y agregarla a la canción (MP3 o MP4).
def descargar_metadata(ruta_del_archivo, nombre_archivo, nombre_artista):
    try:
        # Inicializar cliente de autenticación de Spotify
        client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        # Buscar la canción en Spotify
        resultados = sp.search(
            q=f"{nombre_archivo} {nombre_artista}", type="track", limit=1
        )

        if resultados["tracks"]["items"]:
            track = resultados["tracks"]["items"][0]
            if track["album"]["images"]:
                # Obtener la URL de la carátula del álbum
                url_artwork = track["album"]["images"][0]["url"]
                nombre_artistas = obtener_nombre_artistas(track)

                # Determine el formato de archivo (mp3 o mp4)
                formato_archivo = os.path.splitext(ruta_del_archivo)[1].lower()

                if formato_archivo == ".mp3":
                    # Agregar la portada a los metadatos de la canción (mp3)
                    audio = ID3(ruta_del_archivo)
                    audio.add(
                        APIC(
                            encoding=3,
                            mime="image/jpeg",
                            type=3,
                            desc="Cover",
                            data=requests.get(url_artwork).content,
                        )
                    )

                    # Agregar los nombres de los artistas a los metadatos
                    audio.add(TPE1(encoding=3, text=nombre_artistas))

                    # Intentar obtener el nombre del álbum completo de la API de Spotify
                    nombre_album = obtener_nombre_album(sp, track["album"]["id"])
                    if nombre_album:
                        audio.add(TALB(encoding=3, text=nombre_album))

                    # Agregar el año de publicación si está disponible
                    if "album" in track and "release_date" in track["album"]:
                        audio.add(
                            TYER(encoding=3, text=track["album"]["release_date"][:4])
                        )

                    audio.save()

                elif formato_archivo == ".mp4":
                    # Agregar la portada, los nombres de los artistas, el nombre del álbum y el año de publicación a los metadatos de la canción (MP4)
                    mp4 = MP4(ruta_del_archivo)
                    mp4["\xa9nam"] = nombre_archivo  # Nombre de la canción
                    mp4["\xa9ART"] = nombre_artistas  # Nombre de los artistas
                    mp4["covr"] = [
                        MP4Cover(
                            data=requests.get(url_artwork).content,
                            imageformat=MP4Cover.FORMAT_JPEG,
                        )
                    ]  # Portada

                    # Intentar obtener el nombre del álbum completo de la API de Spotify
                    nombre_album = obtener_nombre_album(sp, track["album"]["id"])
                    if nombre_album:
                        mp4["\xa9alb"] = nombre_album

                    # Agregar el año de publicación si está disponible
                    if "album" in track and "release_date" in track["album"]:
                        mp4["\xa9day"] = track["album"]["release_date"][:4]

                    mp4.save()

                else:
                    print("Formato de archivo no compatible.")

    except Exception as e:
        print(f"❌ Ocurrió un error al descargar la portada y los artistas: {e}\n")


# ------------------------------ #


# Función principal para descargar el audio de un video de YouTube.
def descargar_audio(url):
    global audios_exito, audios_error
    try:
        yt = YouTube(url)
        titulo_original = yt.title
        canal_youtube = yt.author

        caracteres_especiales = ':/\\|?*"<>'

        # Limpiar tanto el título como el canal
        titulo_limpio = "".join(
            c if c not in caracteres_especiales else " " for c in titulo_original
        )

        canal_limpio = "".join(
            c if c not in caracteres_especiales else " " for c in canal_youtube
        )

        carpeta_descarga = config["Directorio"]

        if carpeta_descarga == "/":
            carpeta_descarga = os.path.dirname(os.path.abspath(__file__))

        carpeta_audio = os.path.join(carpeta_descarga, "Audio")
        crear_carpeta(carpeta_audio)
        archivo_audio = os.path.join(
            carpeta_audio, f"{titulo_limpio} - {canal_limpio}.mp3"
        )
        archivo_audio = os.path.normpath(archivo_audio)

        if not archivo_duplicado(
            carpeta_descarga, "Audio", f"{titulo_limpio} - {canal_limpio}.mp3"
        ):
            print(f"🡳  Descargando audio de: '{titulo_original}'...")

            streams_disponibles = (
                yt.streams.filter(only_audio=True).order_by("abr").desc()
            )

            if config["Calidad_audio_video"] == "max":
                # Intentar obtener 360kbps, si no está disponible, elegir la tasa de bits más alta
                stream_seleccionado = (
                    streams_disponibles.filter(abr="360kbps").first()
                    or streams_disponibles.first()
                )
            elif config["Calidad_audio_video"] == "min":
                # Elegir la tasa de bits más baja disponible
                stream_seleccionado = streams_disponibles.last()
            elif config["Calidad_audio_video"] == "avg":
                # Intentar obtener 128kbps, si no está disponible, elegir una tasa de bits menor a 128kbps que no sea la última
                stream_seleccionado = (
                    streams_disponibles.filter(abr="128kbps").first()
                    or streams_disponibles.filter(
                        abr__lt="128kbps", abr__ne=streams_disponibles.last().abr
                    ).first()
                    or streams_disponibles.last()
                )

            # Descargar la corriente seleccionada directamente con el nombre del archivo MP3 final
            stream_seleccionado.download(
                output_path=carpeta_audio,
                filename=f"{titulo_limpio} - {canal_limpio}.mp3",
            )

            audio = AudioSegment.from_file(archivo_audio)
            audio.export(
                archivo_audio,
                format="mp3",
                bitrate=stream_seleccionado.abr.replace("kbps", "k"),
            )

            if config["Scrappear_metadata_Spotify"]:
                nombre_artista = obtener_artista_youtube(url)
                descargar_metadata(archivo_audio, titulo_limpio, nombre_artista)

            audios_exito += 1
            print(
                f"✔️  Se ha descargado '{titulo_original}' con éxito en {stream_seleccionado.abr}.\n"
            )
        else:
            print(
                f"✘ Salteando '{titulo_original}' debido a que ya se ha descargado...\n"
            )

    except Exception as e:
        print(f"❌ Ocurrió un error al descargar el audio: {e}\n")
        audios_error += 1


# ------------------------------ #


# Función para descargar el video de YouTube y agregar la portada y los artistas a la metadata.
def descargar_video(url):
    global videos_exito, videos_error
    try:
        yt = YouTube(url)
        titulo_original = yt.title
        canal_youtube = yt.author

        caracteres_especiales = ':/\\|?*"<>'

        # Limpiar tanto el título como el canal
        titulo_limpio = "".join(
            c if c not in caracteres_especiales else " " for c in titulo_original
        )

        canal_limpio = "".join(
            c if c not in caracteres_especiales else " " for c in canal_youtube
        )

        carpeta_descarga = config["Directorio"]

        if carpeta_descarga == "/":
            carpeta_descarga = os.path.dirname(os.path.abspath(__file__))

        carpeta_video = os.path.join(carpeta_descarga, "Video")
        crear_carpeta(carpeta_video)
        archivo_mp4 = os.path.join(
            carpeta_video, f"{titulo_limpio} - {canal_limpio}.mp4"
        )
        archivo_mp4 = os.path.normpath(archivo_mp4)

        if not archivo_duplicado(
            carpeta_descarga, "Video", f"{titulo_limpio} - {canal_limpio}.mp4"
        ):
            print(f"🡳  Descargando video de: '{titulo_original}'...")

            # Obtener todas las streams disponibles (sin filtrar por formato)
            streams_disponibles = (
                yt.streams.filter(file_extension="mp4", progressive=True)
                .order_by("resolution")
                .desc()
            )

            stream_seleccionado = None
            if config["Calidad_audio_video"] == "max":
                stream_seleccionado = streams_disponibles.first()
            elif config["Calidad_audio_video"] == "min":
                stream_seleccionado = streams_disponibles.last()
            elif config["Calidad_audio_video"] == "avg":
                # Obtener la primera stream disponible de 720p, 480p, 360p o la resolución más baja si no es posible encontrar ninguna
                stream_seleccionado = (
                    streams_disponibles.filter(res="720p")
                    or streams_disponibles.filter(res="480p")
                    or streams_disponibles.filter(res="360p")
                    or [streams_disponibles.last()]
                ).first()

            # Descargar el video con audio incorporado
            if stream_seleccionado:
                stream_seleccionado.download(
                    output_path=carpeta_video, filename=f"{titulo_limpio}.mp4"
                )

                if config["Scrappear_metadata_Spotify"]:
                    # Obtener el nombre del artista del video de YouTube
                    nombre_artista = obtener_artista_youtube(url)

                    # Llamar a la función para descargar la portada y agregarla al video
                    descargar_metadata(archivo_mp4, titulo_limpio, nombre_artista)

                # Aumentar los videos descargados en 1
                videos_exito += 1

                print(
                    f"✔️  Se ha descargado '{titulo_original}' con éxito en la resolución {stream_seleccionado.resolution}.\n"
                )
            else:
                print(
                    f"❌ No se encontró una calidad adecuada para la descarga del video '{titulo_original}'. Inténtalo de nuevo más tarde.\n"
                )

        else:
            print(
                f"✘ Salteando '{titulo_original}' debido a que ya se ha descargado...\n"
            )

    except Exception as e:
        print(f"❌ Ocurrió un error al descargar el video: {e}\n")
        # Aumentar los videos fallidos en 1
        videos_error += 1


# ------------------------------ #


# Función para buscar la canción en el motor de búsqueda de YouTube y devolver el link.
def buscar_cancion_youtube(query):
    try:
        busqueda_videos = VideosSearch(f"{query.title()} Oficial", limit=1)
        resultado = busqueda_videos.result()
        if resultado["result"]:
            link_youtube = resultado["result"][0]["link"]
            print("✔️  Video de YouTube obtenido.\n")
            return link_youtube  # Devolver la URL para su uso posterior

        else:
            print(
                "❌ Ocurrió un error al obtener el video de YouTube, intente de nuevo.\n"
            )
            return ""  # Devolver una lista vacía si no se encuentra el video

    except Exception as e:
        print(f"❌ Ocurrió un error al buscar el video: {e}\n")
        return ""  # Devolver una lista vacía en caso de error


# ------------------------------ #


# Función para obtener los videos de una playlist de YouTube o Spotify en un archivo de texto.
def obtener_playlist(plataforma, playlist_url):
    try:
        print(f"↻ Obteniendo canciones de la playlist de {plataforma}...")

        urls = []

        if plataforma == "YouTube":
            playlist = Playlist(playlist_url)
            for url_video in playlist.video_urls:
                urls.append(url_video)

        elif plataforma == "Spotify":
            client_credentials_manager = SpotifyClientCredentials(
                client_id, client_secret
            )
            sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

            canciones_totales = []
            offset = 0
            while True:
                resultados = sp.playlist_items(playlist_url, offset=offset)
                if not resultados["items"]:
                    break

                for item in resultados["items"]:
                    track = item["track"]
                    canciones_totales.append(
                        (track["name"], track["artists"][0]["name"])
                    )

                offset += len(resultados["items"])
                if offset >= resultados["total"]:
                    break

            links_youtube = []
            for nombre_cancion, nombre_artista in canciones_totales:
                query = f"{nombre_cancion} {nombre_artista} Oficial"
                busqueda_videos = VideosSearch(query, limit=1)
                resultado_video = busqueda_videos.result()["result"][0]
                link_youtube = (
                    "https://www.youtube.com/watch?v=" + resultado_video["id"]
                )
                links_youtube.append(link_youtube)

            urls.extend(links_youtube)

        print(
            f"✔️  Se han obtenido {len(urls)} video(s) de la playlist de {plataforma}.\n"
        )
        return urls

    except Exception as e:
        print(
            f"❌ Ocurrió un error al obtener los video(s) de la playlist de {plataforma}: {e}"
        )
        return ""


# ------------------------------ #


# Función para obtener el link de YouTube de una canción de Spotify.
def obtener_cancion_Spotify(link_spotify):
    try:
        client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        if "open.spotify.com/intl-es/track/" not in link_spotify:
            print("❌ Por favor ingrese un enlace válido de una canción de Spotify.")
            return ""
        else:
            track_id = link_spotify.split("/track/")[1].split("?")[0]
            track_info = sp.track(track_id)
            nombre_cancion = track_info["name"]
            nombre_artista = track_info["artists"][0]["name"]
            query = f"{nombre_cancion} {nombre_artista} Oficial"
            busqueda_videos = VideosSearch(query, limit=1)
            resultado = busqueda_videos.result()
            if resultado["result"]:
                link_youtube = resultado["result"][0]["link"]
                print("✔️  Canción de Spotify obtenida.\n")
                return link_youtube
            else:
                print(
                    "❌ Ocurrió un error al obtener el video de Spotify, intente de nuevo."
                )
                return ""

    except Exception as e:
        print(f"❌ Ocurrió un error al obtener el video de Spotify: {e}")
        return ""


# ------------------------------ #


# Función para editar el archivo config.json directamente desde la ejecución del programa.
def editar_config():
    while True:
        limpiar_pantalla()
        print("📝 Mostrando configuración...")

        with open("config.json", "r") as f:
            config = json.load(f)

        # Mostrar cada clave y su valor correspondiente
        index = 1
        for key, value in config.items():
            print(f"    {index} - {key}: {value}")
            index += 1

        modificar = input(
            "Ingrese el número de la configuración que desea modificar -> "
        )

        # Verificar si la entrada es un número válido
        try:
            opcion = int(modificar)
            if opcion < 1 or opcion > len(config):
                print("Opción no válida")
            else:
                # Obtener la clave correspondiente al número ingresado
                clave_a_modificar = list(config.keys())[opcion - 1]
                valor_a_modificar = list(config.values())[opcion - 1]

                # Verificar si es un Booleano
                if isinstance(valor_a_modificar, bool):
                    nuevo_valor = not valor_a_modificar
                    config[clave_a_modificar] = nuevo_valor

                    # Aplicar los cambios en el Json
                    with open("config.json", "w") as f:
                        json.dump(config, f, indent=4)
                else:
                    if clave_a_modificar == "Calidad_audio_video":
                        while True:
                            nuevo_valor = input(
                                f"Ingrese el nuevo valor para '{clave_a_modificar}'. Valores disponibles: max, min, avg -> "
                            )
                            if (
                                nuevo_valor == "max"
                                or nuevo_valor == "min"
                                or nuevo_valor == "avg"
                            ):
                                break
                            print(
                                "❌ Ocurrió un error al guardar el archivo. Valores disponibles: max, min, avg"
                            )
                    else:
                        nuevo_valor = input(
                            f"Ingrese el nuevo valor para '{clave_a_modificar}' -> "
                        )
                    config[clave_a_modificar] = nuevo_valor

                    with open("config.json", "w") as f:
                        json.dump(config, f, indent=4)

                print(
                    f"'{clave_a_modificar}' se ha sido modificado a '{nuevo_valor}' con éxito."
                )

        except ValueError:
            print("Por favor, ingrese un número.")

        repetir = input("¿Desea modificar algo más? (S/N) -> ").upper()
        if repetir != "S":
            break


# ------------------------------ #


# Función para comprimir los archivos en una carpeta.
def archivos_a_zip(carpeta):
    try:
        archivos = os.listdir(carpeta)
        nombre_zip = os.path.join(carpeta, f"{os.path.basename(carpeta)}.zip")

        # Crear un objeto ZipFile en modo escritura
        with zipfile.ZipFile(nombre_zip, "w") as zipf:
            # Recorrer los archivos y agregarlos al archivo zip
            for archivo in archivos:
                ruta_completa = os.path.join(carpeta, archivo)
                zipf.write(ruta_completa, archivo)

        # Eliminar los archivos originales
        for archivo in archivos:
            ruta_completa = os.path.join(carpeta, archivo)
            os.remove(ruta_completa)

        print(
            "📂 Los archivos en la carpeta '{}' han sido comprimidos.\n".format(
                carpeta.split("\\")[-1]
            )
        )
    except Exception as e:
        print(f"❌ Ocurrió un error al comprimir el archivo: {e}")


# ------------------------------ #


# Inicio del programa.
if __name__ == "__main__":
    limpiar_pantalla()
    tprint("YouTube - Downloader")
    print("Developed by Fvitu")
    print(
        "------------------------------------------------------------------------------------------\n"
    )
    sleep(2)
    limpiar_pantalla()

    print(
        """¿Qué desea hacer?
    1- Descargar
    2- Editar la configuración
          """
    )
    accion = input("Elige una de las opciones -> ")

    if accion == "2":
        editar_config()

        # Actualizar los datos
        with open("config.json", "r") as f:
            config = json.load(f)

    limpiar_pantalla()

    # Lista con todas las urls a descargar
    urls = []

    # Descargar videos de una lista de reproducción de YouTube
    if config["Utilizar_playlist_YouTube"]:
        plataforma = "YouTube"
        urls.extend(
            obtener_playlist(
                plataforma,
                input(
                    f"🔗 Ingrese la url de la lista de reproducción de {plataforma}: "
                ),
            )
        )

    # Descargar videos de una lista de reproducción de Spotify
    if config["Utilizar_playlist_Spotify"]:
        plataforma = "Spotify"
        urls.extend(
            obtener_playlist(
                plataforma,
                input(
                    f"🔗 Ingrese la url de la lista de reproducción de {plataforma}: "
                ),
            )
        )

    # Descargar videos o canciones de un archivo de texto
    if config["Utilizar_canciones.txt"]:
        if os.path.getsize("canciones.txt") != 0:
            with open("canciones.txt", "r") as f:
                urls.extend([line.strip() for line in f])

    # Descargar desde una búsqueda en YouTube
    if config["Busqueda_en_YouTube"]:
        while True:
            url = input(
                "🔍 Ingrese el nombre del video/canción que desea buscar y luego descargar de YouTube (es recomendable agregar el artista también): "
            )
            if url != "":
                break
            else:
                print(
                    "❌ Ocurrió un error al buscar el archivo. Completa el campo de texto para descargar el archivo.\n"
                )
        link_youtube = buscar_cancion_youtube(url)
        urls.append(link_youtube)

    # Descargar desde un enlace de YouTube
    if config["Utilizar_link_de_YouTube"]:
        url = input(
            "🔗 Ingrese la url del video/canción que desea descargar de YouTube: "
        )
        urls.append(url)

    # Descargar desde un enlace de Spotify
    if config["Utilizar_link_de_Spotify"]:
        url = input("🔗 Ingrese la url de la canción que desea descargar de Spotify: ")
        url_spotify = obtener_cancion_Spotify(url)
        urls.append(url_spotify)

    # Función para procesar la descarga basada en la configuración
    def procesar_descargas(urls):
        for url in urls:
            if config["Descargar_video"] and config["Descargar_audio"]:
                # Descargar tanto el video como el audio si está habilitado
                descargar_video(url)
                descargar_audio(url)

            elif config["Descargar_video"]:
                # Descargar solo el video si está habilitado
                descargar_video(url)

            elif config["Descargar_audio"]:
                # Descargar solo el audio si está habilitado
                descargar_audio(url)

        # Comprimir la carpeta de Videos o Audios si está habilitado
        if config["Descargar_video"] and config["Convertir_a_zip"]:
            archivos_a_zip(os.path.abspath("Video"))

        if config["Descargar_audio"] and config["Convertir_a_zip"]:
            archivos_a_zip(os.path.abspath("Audio"))

    # Procesar todas las descargas
    procesar_descargas(urls)

    if config["Eliminar_canciones.txt_automaticamente"]:
        try:
            with open("canciones.txt", "w") as f:
                f.truncate()
        except:
            print(
                "❌ No se pudo vaciar 'canciones.txt' ya que no existe o se lo pudo encontrar."
            )

    if audios_exito >= 1 and videos_exito >= 1:
        print(
            f"✔️  Se han descargado {audios_exito} audios y {videos_exito} videos con éxito."
        )
    elif audios_exito >= 1:
        print(f"✔️  Se han descargado {audios_exito} audios con éxito.")
    elif videos_exito >= 1:
        print(f"✔️  Se han descargado {videos_exito} videos con éxito.")
    elif audios_error > 0 or videos_error > 0:
        print(
            f"❌ Han ocurrido {audios_error + videos_error} errores, de los cuales {audios_error} eran audios y {videos_error} eran videos."
        )

    input("Presiona 'Enter' para finalizar la ejecución.")
