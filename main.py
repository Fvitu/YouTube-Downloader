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
import spotipy
import shutil
import json
import os


# ------------------------------ #


audios_exito = 0
audios_error = 0

videos_exito = 0
videos_error = 0


# ------------------------------ #


# Función para eliminar la consola dependiendo del sistema operativo
def limpiar_pantalla():
    if system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


# ------------------------------ #


try:
    # Verificar si existe el archivo de configuración
    with open("config.json", "r") as f:
        config = json.load(f)

    client_id = config["Client_ID"]
    client_secret = config["Secret_ID"]

except:
    # Si no existe, crearlo con la configuración por defecto y salir del programa para que el usuario lo configure
    config = {
        "Client_ID": "",  # f8068cf75621448184edc11474e60436
        "Secret_ID": "",  # 243ded973fcd495f989ff84ae9e28669
        "Directorio": "/",
        "Resolucion_video": "ave",
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
            f.write(
                "Si quieres puedes utilizar este archivo para descargar videos/canciones masivamente. Solo tienes que eliminar esta linea y agregar las url's del video de YouTube una debajo de la otra."
            )
else:
    if os.path.exists("canciones.txt"):
        os.remove("canciones.txt")


# ------------------------------ #


def crear_carpeta(carpeta):
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)


# ------------------------------ #


# Función para mover archivos a una carpeta específica
def mover_archivo(cancion, carpeta):
    mp4_path = os.path.join(carpeta, cancion)
    shutil.move(cancion, mp4_path)


# ------------------------------ #


# Función para verificar si el archivo ya existe
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


# Función para obtener el nombre del artista de YouTube
def obtener_artista_youtube(url):
    try:
        yt = YouTube(url)
        return yt.author if yt.author else ""
    except Exception as e:
        print(f"❌ Ocurrió un error al obtener el nombre del artista de YouTube: {e}")
        return ""


# ------------------------------ #


# Función para obtener los nombres de los artistas como una cadena separada por comas
def obtener_nombre_artistas(track):
    if track["artists"]:
        artists = [artist["name"] for artist in track["artists"]]
        return ", ".join(artists)
    return ""


# ------------------------------ #


# Función para obtener el nombre del álbum completo desde la API de Spotify
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


# Función para descargar la portada y agregarla a la canción (MP3 o MP4)
def descargar_metadata(ruta_del_archivo, nombre_archivo, nombre_artista):
    try:
        # Obtenga la URL de la portada del álbum y los nombres de los artistas de Spotify
        client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        resultados = sp.search(
            q=f"{nombre_archivo} {nombre_artista}", type="track", limit=1
        )

        if resultados["tracks"]["items"]:
            track = resultados["tracks"]["items"][0]
            if track["album"]["images"]:
                url_artwork = track["album"]["images"][0]["url"]
                nombre_artistas = obtener_nombre_artistas(track)

                # Determine el formato de archivo (mp3 o mp4)
                formato_archivo = os.path.splitext(ruta_del_archivo)[1].lower()

                if formato_archivo == ".mp3":
                    # Agregue la portada a los metadatos de la canción (mp3)
                    audio = ID3(ruta_del_archivo)
                    audio.add(
                        APIC(
                            3,
                            "image/jpeg",
                            3,
                            "Front cover",
                            requests.get(url_artwork).content,
                        )
                    )

                    # Agregue los nombres de los artistas a los metadatos
                    audio.add(TPE1(encoding=3, text=nombre_artistas))

                    # Intenta obtener el nombre del álbum completo de la API de Spotify
                    nombre_album = obtener_nombre_album(sp, track["album"]["id"])
                    if nombre_album:
                        audio.add(TALB(encoding=3, text=nombre_album))

                    # Agregue el año de publicación si está disponible
                    if "album" in track and "release_date" in track["album"]:
                        audio.add(
                            TYER(encoding=3, text=track["album"]["release_date"][:4])
                        )

                    audio.save()

                elif formato_archivo == ".mp4":
                    # Agregue la portada, los nombres de los artistas, el nombre del álbum y el año de publicación a los metadatos de la canción (MP4)
                    mp4 = MP4(
                        ruta_del_archivo
                    )  # Usar ruta_del_archivo en lugar de nombre_archivo
                    mp4["\xa9nam"] = nombre_archivo  # Nombre de la canción
                    mp4["\xa9ART"] = nombre_artistas  # Nombre de los artistas
                    mp4["covr"] = [
                        MP4Cover(
                            requests.get(url_artwork).content, MP4Cover.FORMAT_JPEG
                        )
                    ]  # Portada

                    # Intenta obtener el nombre del álbum completo de la API de Spotify
                    nombre_album = obtener_nombre_album(sp, track["album"]["id"])
                    if nombre_album:
                        mp4["\xa9alb"] = nombre_album

                    # Agregue el año de publicación si está disponible
                    if "album" in track and "release_date" in track["album"]:
                        mp4["\xa9day"] = track["album"]["release_date"][:4]

                    mp4.save()

                else:
                    print("Formato de archivo no compatible.")

    except Exception as e:
        print(f"❌ Ocurrió un error al descargar la portada y los artistas: {e}\n")


# ------------------------------ #


# Función principal para descargar el audio de un video de YouTube
def descargar_audio(url):
    global audios_exito, audios_error
    try:
        yt = YouTube(url)
        titulo_original = yt.title

        # Comprobar si tiene caracteres especiales
        caracteres_especiales = ':/\\|?*"<>'
        titulo_limpio = "".join(
            c if c not in caracteres_especiales else " " for c in titulo_original
        )

        carpeta_descarga = config["Directorio"]

        # Si la carpeta de descarga es '/' entonces se descargará en la carpeta actual
        if carpeta_descarga == "/":
            carpeta_descarga = os.path.dirname(os.path.abspath(__file__))

        carpeta_audio = os.path.join(carpeta_descarga, "Audio")
        crear_carpeta(carpeta_audio)
        archivo_audio = os.path.join(
            carpeta_audio, f"{titulo_limpio}.mp3"
        )  # Siempre en formato MP3
        archivo_audio = os.path.normpath(archivo_audio)

        # Si el archivo no se ha descargado, entonces se descargará
        if not archivo_duplicado(carpeta_descarga, "Audio", f"{titulo_limpio}.mp3"):
            print(f"🡳  Descargando audio de: '{titulo_original}'...")
            stream = yt.streams.filter(only_audio=True).first()

            # Descargar el archivo directamente en la carpeta de destino
            archivo_temporal = os.path.join(carpeta_audio, stream.default_filename)
            stream.download(output_path=carpeta_audio)

            # Siempre utilizar FFMPEG para convertir el archivo a MP3
            audio = AudioSegment.from_file(archivo_temporal, format="mp4")
            audio.export(archivo_audio, format="mp3")
            os.remove(archivo_temporal)  # Eliminar el archivo MP4 original

            if config["Scrappear_metadata_Spotify"]:
                # Obtener el nombre del artista del video de YouTube
                nombre_artista = obtener_artista_youtube(url)

                # Llamar a la función para descargar la portada y agregarla a la canción
                descargar_metadata(
                    archivo_audio, titulo_limpio, nombre_artista
                )  # Pasa la ruta completa del archivo descargado

            # Aumentar los audios descargados en 1
            audios_exito += 1

            print(f"✔️  Se ha descargado '{titulo_original}' con éxito.\n")
        else:
            print(
                f"✘ Salteando '{titulo_original}' debido a que ya se ha descargado...\n"
            )

    except Exception as e:
        print(f"❌ Ocurrió un error al descargar el audio: {e}\n")
        # Aumentar los audios fallidos en 1
        audios_error += 1


# ------------------------------ #


# Función para descargar el video de YouTube y agregar la portada y los artistas a la metadata
def descargar_video(url):
    global videos_exito, videos_error
    try:
        yt = YouTube(url)
        titulo_original = yt.title

        caracteres_especiales = ':/\\|?*"<>'
        titulo_limpio = "".join(
            c if c not in caracteres_especiales else " " for c in titulo_original
        )

        carpeta_descarga = config["Directorio"]

        if carpeta_descarga == "/":
            carpeta_descarga = os.path.dirname(os.path.abspath(__file__))

        carpeta_video = os.path.join(carpeta_descarga, "Video")
        crear_carpeta(carpeta_video)
        archivo_mp4 = os.path.join(carpeta_video, f"{titulo_limpio}.mp4")
        archivo_mp4 = os.path.normpath(archivo_mp4)

        if not archivo_duplicado(carpeta_descarga, "Video", f"{titulo_limpio}.mp4"):
            print(f"🡳  Descargando video de: '{titulo_original}'...")

            # Obtener todas las streams disponibles (sin filtrar por formato)
            available_streams = yt.streams.order_by("resolution").desc()

            if config["Resolucion_video"] == "max":
                selected_stream = available_streams.first()
            elif config["Resolucion_video"] == "min":
                selected_stream = available_streams.last()
            elif config["Resolucion_video"] == "ave":
                # Intentar obtener 720p, si no está disponible, elegir la resolución más baja
                selected_stream = (
                    available_streams.filter(res="720p").first()
                    or available_streams.last()
                )

            selected_stream.download(
                output_path=carpeta_video, filename=f"{titulo_limpio}.mp4"
            )

            archivo_temporal = os.path.join(carpeta_video, f"{titulo_limpio}.mp4")

            if config["Scrappear_metadata_Spotify"]:
                # Obtener el nombre del artista del video de YouTube
                artist_name = obtener_artista_youtube(url)

                # Llamar a la función para descargar la portada y agregarla al video
                descargar_metadata(archivo_temporal, titulo_limpio, artist_name)

            # Aumentar los videos descargados en 1
            videos_exito += 1

            print(
                f"✔️  Se ha descargado '{titulo_original}' con éxito en la resolución {selected_stream.resolution}.\n"
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


def buscar_cancion_youtube(query):
    try:
        busqueda_videos = VideosSearch(f"{query.title()} Oficial", limit=1)
        resultado = busqueda_videos.result()
        if resultado["result"]:
            link_youtube = resultado["result"][0]["link"]
            print("✔️  Video de YouTube obtenido.")
            return [link_youtube]  # Devolver la URL en una lista para su uso posterior

        else:
            print(
                "❌ Ocurrió un error al obtener el video de YouTube, intente de nuevo."
            )
            return []  # Devolver una lista vacía si no se encuentra el video

    except Exception as e:
        print(f"❌ Ocurrió un error al buscar el video: {e}\n")
        return []  # Devolver una lista vacía en caso de error


# ------------------------------ #


# Función para obtener los videos de una playlist de YouTube o Spotify en un archivo de texto
def obtener_playlist(plataforma, playlist_url):
    try:
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
        return []


# ------------------------------ #


# Función para obtener el link de YouTube de una canción de Spotify
def obtener_cancion_Spotify(link_spotify):
    try:
        client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        if "open.spotify.com/intl-es/track/" not in link_spotify:
            print("❌ Por favor ingrese un enlace válido de una canción de Spotify.")
            return []
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
                return [link_youtube]
            else:
                print(
                    "❌ Ocurrió un error al obtener el video de Spotify, intente de nuevo."
                )
                return []

    except Exception as e:
        print(f"❌ Ocurrió un error al obtener el video de Spotify: {e}")
        return []


# ------------------------------ #


def editar_config():
    while True:
        limpiar_pantalla()
        print("📝 Mostrando configuración...")

        with open("config.json", "r") as file:
            config = json.load(file)

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
                    with open("config.json", "w") as file:
                        json.dump(config, file, indent=4)
                else:
                    nuevo_valor = input(
                        f"Ingrese el nuevo valor para '{clave_a_modificar}': "
                    )
                    config[clave_a_modificar] = nuevo_valor

                    with open("config.json", "w") as file:
                        json.dump(config, file, indent=4)

                print(
                    f"'{clave_a_modificar}' se ha sido modificado a '{nuevo_valor}' con éxito."
                )

        except ValueError:
            print("Por favor, ingrese un número.")

        repetir = input("¿Desea modificar algo más? (S/N) ->").upper()
        if repetir != "S":
            break


# ------------------------------ #


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

        client_id = config["Client_ID"]
        client_secret = config["Secret_ID"]

    limpiar_pantalla()

    # Función para procesar la descarga basada en la configuración
    def procesar_descargas(urls, descargar_funcion):
        if urls:
            for url in urls:
                descargar_funcion(url)

    # Descargar videos de una lista de reproducción de YouTube o Spotify
    if config["Utilizar_playlist_YouTube"] or config["Utilizar_playlist_Spotify"]:
        plataforma = "YouTube" if config["Utilizar_playlist_YouTube"] else "Spotify"
        urls = obtener_playlist(
            plataforma,
            input(f"🔗 Ingrese la url de la lista de reproducción de {plataforma}: "),
        )

        if urls:
            procesar_descargas(
                urls, descargar_video if config["Descargar_video"] else descargar_audio
            )

    # Descargar videos o canciones de un archivo de texto
    if config["Utilizar_canciones.txt"]:
        urls = []
        if os.path.getsize("canciones.txt") != 0:
            with open("canciones.txt", "r") as file:
                urls = [line.strip() for line in file]

        procesar_descargas(
            urls, descargar_video if config["Descargar_video"] else descargar_audio
        )

    # Descargar desde una búsqueda en YouTube
    if config["Busqueda_en_YouTube"]:
        url = input(
            "🔍 Ingrese el nombre del video/canción que desea buscar y luego descargar de YouTube (es recomendable agregar el artista también): "
        )
        urls = []

        if config["Descargar_video"] or config["Descargar_audio"]:
            urls = buscar_cancion_youtube(url)

        procesar_descargas(
            urls, descargar_video if config["Descargar_video"] else descargar_audio
        )

    # Descargar desde un enlace de YouTube
    if config["Utilizar_link_de_YouTube"]:
        url = input(
            "🔗 Ingrese la url del video/canción que desea descargar de YouTube: "
        )
        if config["Descargar_video"]:
            descargar_video(url)
        if config["Descargar_audio"]:
            descargar_audio(url)

    # Descargar desde un enlace de Spotify
    if config["Utilizar_link_de_Spotify"]:
        url = input("🔗 Ingrese la url de la canción que desea descargar de Spotify: ")
        urls = []
        if config["Descargar_video"] or config["Descargar_audio"]:
            urls = obtener_cancion_Spotify(url)

        procesar_descargas(
            urls, descargar_video if config["Descargar_video"] else descargar_audio
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
