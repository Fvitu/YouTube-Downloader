from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
from pydub import AudioSegment
from platform import system
from pytube import Playlist
from pytube import YouTube
from time import sleep
from art import *
import spotipy
import shutil
import json
import sys
import os

#------------------------------#


def limpiar_pantalla():
    if system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

#------------------------------#


try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except:
    config = {
        "Descargar_video": False,
        "Descargar_audio": True,
        "Utilizar_playlist_YouTube": False,
        "Utilizar_playlist_Spotify": False,
        "Eliminar_canciones.txt_automaticamente": False,
        "Utilizar_link_de_YouTube": True,
        "Utilizar_link_de_Spotify": False,
        "Utilizar_canciones.txt": False,
        "Utilizar_varias_carpetas": True,
        "Utilizarffmpeg": True,
        "Directorio": "/",
    }
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

    limpiar_pantalla()
    tprint("YouTube - Downloader")
    print("Developed by Fvitu")
    print("------------------------------------------------------------------------------------------\n")
    sleep(2)
    limpiar_pantalla()

    print("Bienvenido a esta aplicación creada por Fvitu, aquí podrá descargar videos o audios de YouTube totalmente gratis y de manera sencilla. Solo tendrá que configurar el archivo llamado 'config.json' para poder utilizar esta aplicación. Gracias")

    if not os.path.exists("canciones.txt"):
        with open("canciones.txt", 'w') as f:
            f.write("Si quieres puedes utilizar este archivo para descargar videos/canciones masivamente. Solo tienes que eliminar esta linea y agregar las url's del video de YouTube una debajo de la otra.")
            f.close()

    exit()

#------------------------------#


if not os.path.exists("canciones.txt"):
    with open("canciones.txt", 'w') as f:
        f.close()

#------------------------------#


if not os.path.exists("descargar.txt"):
    with open("descargar.txt", 'w') as f:
        f.close()

#------------------------------#


def mover_a_canciones(cancion):
    if not os.path.exists('Canciones'):
        os.makedirs('Canciones')

    mp4_path = os.path.join('Canciones', cancion)
    shutil.move(cancion, mp4_path)

#------------------------------#


def mover_a_carpeta(cancion, carpeta):
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    mp4_path = os.path.join(carpeta, cancion)
    shutil.move(cancion, mp4_path)

#------------------------------#


def archivo_duplicado(directorio, tipo, nombre):
    try:
        if directorio == "/":
            directorio = os.path.dirname(os.path.abspath(sys.argv[0]))  # Directorio del script

        if tipo == "Audio":
            directorio = os.path.join(directorio, "Audio")

        if tipo == "Video":
            directorio = os.path.join(directorio, "Video")

        archivos_en_ruta_actual = os.listdir(directorio)

        for archivo in archivos_en_ruta_actual:
            if archivo == nombre:
                return True
    except:
        return False


#------------------------------#


def descargar_audio(url):
    try:
        yt = YouTube(url)
        titulo = yt.title
        carpeta_descarga = config.get("Directorio", "Canciones")  # Obtenemos la carpeta de descarga desde la configuración o usamos "Canciones" por defecto.

        if carpeta_descarga == "/":
            carpeta_descarga = os.path.dirname(os.path.abspath(__file__))  # Directorio del script en lugar de "/"
        
        carpeta_audio = os.path.join(carpeta_descarga, "Audio")
        mp3_file = os.path.join(carpeta_audio, f"{titulo}.mp3")
        mp3_file = os.path.normpath(mp3_file)
        
        if not archivo_duplicado(carpeta_descarga, "Audio", f"{titulo}.mp3"):
            print(f"🡳  Descargando audio de: '{titulo}'...")
            stream = yt.streams.filter(only_audio=True).first()
            stream.download()
            
            if not os.path.exists(carpeta_audio):
                os.makedirs(carpeta_audio)
            
            if config.get("Utilizarffmpeg", False):
                mp4_file = stream.default_filename
                audio = AudioSegment.from_file(mp4_file, format="mp4")
                audio.export(mp3_file, format="mp3")
                os.remove(mp4_file)
            
            else:
                os.rename(stream.default_filename, mp3_file)
            print(f"✔️  Se ha descargado '{titulo}' con éxito.\n")
        
        else:
            print(f"✘ Salteando {titulo} debido a que ya se ha descargado...\n")

    except Exception as e:
        print(f"❌ Ocurrió un error al descargar el audio: {e}\n")

#------------------------------#



def descargar_video(url=False):
    try:
        yt = YouTube(url)
        titulo = yt.title
        carpeta_descarga = config.get("Directorio", "Canciones")

        if carpeta_descarga == "/":
            carpeta_descarga = os.path.dirname(os.path.abspath(__file__))
    
        mp4_file = os.path.join(carpeta_descarga, "Video", f"{titulo}.mp4")
        mp4_file = os.path.normpath(mp4_file)
        
        if not archivo_duplicado(carpeta_descarga, "Video", f"{titulo}.mp4"):
            print(f"🡳  Descargando video de: '{titulo}'...")
            stream = yt.streams.get_highest_resolution()
            stream.download()
            carpeta_video = os.path.join(carpeta_descarga, "Video")

            if not os.path.exists(carpeta_video):
                os.makedirs(carpeta_video)
            
            mover_a_carpeta(stream.default_filename, carpeta_video)
            print(f"✔️  Se ha descargado '{titulo}' con éxito.\n")
        
        else:
            print(f"✘ Salteando {titulo} debido a que ya se ha descargado...\n")
    
    except Exception as e:
        print(f"❌ Ocurrió un error al descargar el video: {e}\n")

#------------------------------#


def obtener_playlist_YouTube(playlists):
    urls = []
    try:
        for playlists in playlists:
            playlist_urls = Playlist(playlists)

        for url in playlist_urls:
            urls.append(url)

        with open("descargar.txt", "w") as f:
            for url in urls:
                f.write(f"{url}\n")

        print("✔️  Videos de la playlist obtenidos.\n")

    except Exception as e:
        print(f"❌ Ocurrió un error al obtener los videos de la playlist de YouTube: {e}")

#------------------------------#


def obtener_playlist_Spotify(playlist_id):
    try:
        client_id = 'f8068cf75621448184edc11474e60436'
        client_secret = '243ded973fcd495f989ff84ae9e28669'
        client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        results = sp.playlist_items(playlist_id)
        songs = []
        for item in results['items']:
            track = item['track']
            songs.append(track['name'])

        youtube_links = []
        for song_name in songs:
            query = song_name + ' Oficial'
            videos_search = VideosSearch(query, limit=1)
            video_result = videos_search.result()['result'][0]
            youtube_link = 'https://www.youtube.com/watch?v=' + \
                video_result['id']
            youtube_links.append(youtube_link)

        with open('descargar.txt', 'w') as f:
            for youtube_link in youtube_links:
                f.write(youtube_link + '\n')

        print("✔️  Videos de la playlist obtenidos.")

    except Exception as e:
        print(f"❌ Ocurrió un error al obtener los videos de la playlist de Spotify: {e}")

#------------------------------#


def obtener_cancion_Spotify(spotify_link):
    client_id = 'f8068cf75621448184edc11474e60436'
    client_secret = '243ded973fcd495f989ff84ae9e28669'
    client_credentials_manager = SpotifyClientCredentials(
        client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    if 'spotify.com/track/' not in spotify_link:
        print("Por favor ingrese un enlace válido de una canción de Spotify.")
    else:
        track_id = spotify_link.split('/track/')[1].split('?')[0]
        track_info = sp.track(track_id)
        song_name = track_info['name']
        query = song_name + ' Official'
        videosSearch = VideosSearch(query, limit=1)
        result = videosSearch.result()
        if result['result']:
            youtube_link = result['result'][0]['link']

            # Guardar el enlace de YouTube en el archivo "descargar.txt"
            with open('descargar.txt', 'a') as f:
                f.write(youtube_link + '\n')
                print("✔️  Video de Spotify obtenido.")
        else:
            print("❌ Ocurrió un error al obtener los videos de la playlist, intente de nuevo.")

#------------------------------#


if __name__ == '__main__':
    limpiar_pantalla()
    tprint("YouTube - Downloader")
    print("Developed by Fvitu")
    print("------------------------------------------------------------------------------------------\n")
    sleep(2)
    limpiar_pantalla()

    if config["Utilizar_playlist_YouTube"]:
        print("Ingrese la url de una lista de reproducción pública/no listada de YouTube que desea descargar:")
        url = input("-> ")
        url = [url]
        print("")
        if config["Descargar_video"] or config["Descargar_audio"]:
            obtener_playlist_YouTube(url)

        if config["Descargar_video"]:
            file = open('descargar.txt', 'r')
            for cancion in file:
                url = cancion
                descargar_video(url)

        if config["Descargar_audio"]:
            file = open('descargar.txt', 'r')
            for cancion in file:
                url = cancion
                descargar_audio(url)

    if config["Utilizar_playlist_Spotify"]:
        print("Ingrese la url de una lista de reproducción pública de Spotify que desea descargar:")
        url = str(input("-> "))
        print("")
        if config["Descargar_video"] or config["Descargar_audio"]:
            obtener_playlist_Spotify(url)

        if config["Descargar_video"]:
            file = open('descargar.txt', 'r')
            for cancion in file:
                url = cancion
                descargar_video(url)

        if config["Descargar_audio"]:
            file = open('descargar.txt', 'r')
            for cancion in file:
                url = cancion
                descargar_audio(url)

    if config["Utilizar_canciones.txt"]:
        if os.path.getsize("canciones.txt") == 0:
            print("Antes de descargar alguna canción, debe de ingresar la url del video que desea descargar en el archivo 'canciones.txt'. \n")

        print("Utilizando archivo 'canciones.txt'...\n")

        if config["Descargar_video"]:
            file = open('canciones.txt', 'r')
            for cancion in file:
                url = cancion
                descargar_video(url)

        if config["Descargar_audio"]:
            file = open('canciones.txt', 'r')
            for cancion in file:
                url = cancion
                descargar_audio(url)

    if config["Utilizar_link_de_YouTube"]:
        print("Ingrese la url del video/canción que desea descargar de YouTube:")
        url = str(input("-> "))
        print("")
        if config["Descargar_video"]:
            descargar_video(url)

        if config["Descargar_audio"]:
            descargar_audio(url)

    if config["Utilizar_link_de_Spotify"]:
        print("Ingrese la url de la canción que desea descargar de Spotify:")
        url = input("-> ")
        print("")
        if config["Descargar_video"] or config["Descargar_audio"]:
            obtener_cancion_Spotify(url)

        if config["Descargar_video"]:
            file = open('descargar.txt', 'r')
            for cancion in file:
                url = cancion
                descargar_video(url)

        if config["Descargar_audio"]:
            file = open('descargar.txt', 'r')
            for cancion in file:
                url = cancion
                descargar_audio(url)

    if config["Eliminar_canciones.txt_automaticamente"]:
        with open('canciones.txt', 'w') as f:
            f.write("")
    with open('descargar.txt', 'w') as f:
        f.write("")

    print("✔️  Las descargas han finalizado correctamente.")