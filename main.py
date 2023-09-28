from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
from mutagen.id3 import ID3, APIC, TPE1
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


#------------------------------#

#Función para eliminar la consola dependiendo del sistema operativo
def limpiar_pantalla():
    if system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


#------------------------------#


try:
    #Verificar si existe el archivo de configuración
    with open('config.json', 'r') as f:
        config = json.load(f)
except:
    #Si no existe, crearlo con la configuración por defecto y salir del programa para que el usuario lo configure
    config = {
        "Descargar_video": False,
        "Descargar_audio": True,
        "Utilizar_playlist_YouTube": False,
        "Utilizar_playlist_Spotify": False,
        "Eliminar_canciones.txt_automaticamente": False,
        "Utilizar_link_de_YouTube": True,
        "Utilizar_link_de_Spotify": False,
        "Utilizar_canciones.txt": False,
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


#Crear el archivo necesario para descargar canciones a través de este archivo de texto
if not os.path.exists("canciones.txt"):
    with open("canciones.txt", 'w') as f:
        f.close()


#------------------------------#


#Crear el archivo necesario para descargar playlists
if not os.path.exists("descargar.txt"):
    with open("descargar.txt", 'w') as f:
        f.close()


#------------------------------#


#Función para mover archivos a la carpeta 'Canciones'
def mover_a_canciones(cancion):
    if not os.path.exists('Canciones'):
        os.makedirs('Canciones')

    mp4_path = os.path.join('Canciones', cancion)
    shutil.move(cancion, mp4_path)


#------------------------------#


#Función para mover archivos a la carpeta 'Videos'
def mover_a_carpeta(cancion, carpeta):
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    mp4_path = os.path.join(carpeta, cancion)
    shutil.move(cancion, mp4_path)


#------------------------------#


#Función para verificar si el archivo ya existe
def archivo_duplicado(directorio, tipo, nombre):
    try:
        if tipo == "Audio":
            carpeta_tipo = "Audio"
        elif tipo == "Video":
            carpeta_tipo = "Video"

        directorio = os.path.join(directorio, carpeta_tipo)

        archivos_en_ruta_actual = os.listdir(directorio)

        for archivo in archivos_en_ruta_actual:
            if archivo == nombre:
                return True
    except:
        return False


#------------------------------#


#Función para obtener los nombres de los artistas como una cadena separada por comas
def get_artist_names(track):
    if track['artists']:
        artists = [artist['name'] for artist in track['artists']]
        return ", ".join(artists)
    return ""


#------------------------------#


#Función para descargar la portada y agregarla a la canción (MP3 o MP4)
def download_song(audio_file_path, song_name, artist_name):
    try:
        #Obtenga la URL de la portada del álbum y los nombres de los artistas de Spotify
        client_id = 'f8068cf75621448184edc11474e60436'
        client_secret = '243ded973fcd495f989ff84ae9e28669'
        client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        results = sp.search(q=f"{song_name} {artist_name}", type='track', limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            if track['album']['images']:
                artwork_url = track['album']['images'][0]['url']
                artist_names = get_artist_names(track)
                
                #Determine el formato de archivo (mp3 o mp4)
                file_format = os.path.splitext(audio_file_path)[1].lower()
                
                if file_format == '.mp3':
                    #Agregue la portada  a los metadatos de la canción (mp3)
                    audio = ID3(audio_file_path)
                    audio.add(APIC(3, 'image/jpeg', 3, 'Front cover', requests.get(artwork_url).content))
                    audio.save()
                    #Agregue los nombres de los artistas a los metadatos
                    audio.add(TPE1(encoding=3, text=artist_names))
                    audio.save()
                elif file_format == '.mp4':
                    #Agregue la portada y los nombres de los artistas a los metadatos de la canción (MP4)
                    mp4 = MP4(audio_file_path)
                    mp4['\xa9nam'] = song_name  #Nombre de la canción
                    mp4['\xa9ART'] = artist_names  #Nombre de los artistas
                    mp4['covr'] = [MP4Cover(requests.get(artwork_url).content, MP4Cover.FORMAT_JPEG)]  #Portada
                    mp4.save()
                else:
                    print("Formato de archivo no compatible.")
                    
    except Exception as e:
        print(f"❌ Ocurrió un error al descargar la portada y los artistas: {e}\n")


#------------------------------#


#Función para descargar el audio de un video de YouTube
def descargar_audio(url):
    try:
        yt = YouTube(url)
        titulo_original = yt.title

        #Comprobar si tiene caracteres especiales
        caracteres_especiales = ':/\\|?*"<>'
        titulo_limpio = ''.join(c if c not in caracteres_especiales else ' ' for c in titulo_original)

        carpeta_descarga = config.get("Directorio", "Canciones")

        #Si la carpeta de descarga es '/' entonces se descargará en la carpeta actual
        if carpeta_descarga == "/":
            carpeta_descarga = os.path.dirname(os.path.abspath(__file__))

        carpeta_audio = os.path.join(carpeta_descarga, "Audio")
        audio_file = os.path.join(carpeta_audio, f"{titulo_limpio}.mp3")  #Siempre en formato MP3
        audio_file = os.path.normpath(audio_file)

        #Si el archivo no se ha descargado, entonces se descargará
        if not archivo_duplicado(carpeta_descarga, "Audio", f"{titulo_limpio}.mp3"):
            print(f"🡳  Descargando audio de: '{titulo_original}'...")
            stream = yt.streams.filter(only_audio=True).first()

            #Descargar el archivo directamente en la carpeta de destino
            archivo_temporal = os.path.join(carpeta_audio, stream.default_filename)
            stream.download(output_path=carpeta_audio)

            #Siempre utilizar FFMPEG para convertir el archivo a MP3
            audio = AudioSegment.from_file(archivo_temporal, format="mp4")
            audio.export(audio_file, format="mp3")
            os.remove(archivo_temporal)  #Eliminar el archivo MP4 original

            print(f"✔️  Se ha descargado '{titulo_original}' con éxito.\n")
            
            #Llamar a la función para descargar la portada y agregarla a la canción
            download_song(audio_file, titulo_limpio, "")  #Pasa la ruta completa del archivo descargado

        else:
            print(f"✘ Salteando {titulo_original} debido a que ya se ha descargado...\n")

    except Exception as e:
        print(f"❌ Ocurrió un error al descargar el audio: {e}\n")


#------------------------------#


#Función para descargar el video de YouTube y agregar la portada y los artistas a la metadata
def descargar_video(url=False):
    try:
        yt = YouTube(url)
        titulo_original = yt.title

        #Reemplazar la apóstrofe (') en el título con un guion bajo (_) o eliminarla
        titulo_limpio = titulo_original.replace("'", "").strip()

        carpeta_descarga = config.get("Directorio", "Canciones")

        #Si la carpeta de descarga es '/' entonces se descargará en la carpeta actual
        if carpeta_descarga == "/":
            carpeta_descarga = os.path.dirname(os.path.abspath(__file__))

        #Crear la carpeta 'Video' si no existe y establecer el nombre del archivo
        mp4_file = os.path.join(carpeta_descarga, "Video", f"{titulo_limpio}.mp4")
        mp4_file = os.path.normpath(mp4_file)

        #Almacena la ubicación del archivo de video antes de realizar la descarga
        video_file_path = mp4_file

        #Si el archivo no se ha descargado, entonces se descargará
        if not archivo_duplicado(carpeta_descarga, "Video", f"{titulo_limpio}.mp4"):
            print(f"🡳  Descargando video de: '{titulo_original}'...")
            stream = yt.streams.get_highest_resolution()
            stream.download()
            carpeta_video = os.path.join(carpeta_descarga, "Video")

            #Crear la carpeta 'Video' si no existe
            if not os.path.exists(carpeta_video):
                os.makedirs(carpeta_video)

            #Cambiar el nombre del archivo descargado para que coincida con el título limpio
            nuevo_nombre_archivo = os.path.join(carpeta_video, f"{titulo_limpio}.mp4")
            os.rename(stream.default_filename, nuevo_nombre_archivo)
            
            print(f"✔️  Se ha descargado '{titulo_original}' con éxito.\n")
            
            #Llamar a la función para descargar la portada y agregarla a la canción
            download_song(video_file_path, titulo_limpio, "")  #Pasa la ruta completa del archivo MP4

        else:
            print(f"✘ Salteando {titulo_original} debido a que ya se ha descargado...\n")

    except Exception as e:
        print(f"❌ Ocurrió un error al descargar el video: {e}\n")


#------------------------------#


#Función para obtener los videos de una playlist de YouTube en un archivo de texto para obtener asi, su url
def obtener_playlist_YouTube(playlists):
    urls = []
    try:
        for playlists in playlists:
            playlist_urls = Playlist(playlists)

        for url in playlist_urls:
            urls.append(url)

        #Guardar los links en un archivo de texto
        with open("descargar.txt", "w") as f:
            for url in urls:
                f.write(f"{url}\n")

        print("✔️  Se han obtenido", len(urls), "videos de la playlist de YouTube.\n")

    except Exception as e:
        print(f"❌ Ocurrió un error al obtener los videos de la playlist de YouTube: {e}")


#------------------------------#


#Función para obtener los videos de una playlist de Spotify en un archivo de texto para obtener asi, su url
def obtener_playlist_Spotify(playlist_id):
    try:
        #Establecer las credenciales de Spotify
        client_id = 'f8068cf75621448184edc11474e60436'
        client_secret = '243ded973fcd495f989ff84ae9e28669'
        client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        #Hacer tantas peticiones como sea necesario para obtener todas las canciones de la playlist
        total_songs = []
        offset = 0
        while True:
            results = sp.playlist_items(playlist_id, offset=offset)
            if not results['items']:
                break

            for item in results['items']:
                track = item['track']
                total_songs.append((track['name'], track['artists'][0]['name']))

            offset += len(results['items'])
            if offset >= results['total']:
                break

        #Conseguir el link de YouTube de cada canción
        youtube_links = []
        for song_name, artist_name in total_songs:
            query = f"{song_name} {artist_name} Oficial"
            videos_search = VideosSearch(query, limit=1)
            video_result = videos_search.result()['result'][0]
            youtube_link = 'https://www.youtube.com/watch?v=' + video_result['id']
            youtube_links.append(youtube_link)

        #Guardar los links en un archivo de texto
        with open('descargar.txt', 'w') as f:
            for youtube_link in youtube_links:
                f.write(youtube_link + '\n')

        print("✔️  Se han obtenido", len(total_songs), "videos de la playlist de Spotify.\n")

    except Exception as e:
        print(f"❌ Ocurrió un error al obtener los videos de la playlist de Spotify: {e}")


#------------------------------#


#Función para obtener el link de YouTube de una canción de Spotify
def obtener_cancion_Spotify(spotify_link):
    try:
        #Establecer las credenciales de Spotify
        client_id = 'f8068cf75621448184edc11474e60436'
        client_secret = '243ded973fcd495f989ff84ae9e28669'
        client_credentials_manager = SpotifyClientCredentials(
            client_id, client_secret)
        sp = spotipy.Spotify(
            client_credentials_manager=client_credentials_manager)

        if 'spotify.com/track/' not in spotify_link:
            print("❌ Por favor ingrese un enlace válido de una canción de Spotify.")
        else:
            #Obtener el link de YouTube de la canción
            track_id = spotify_link.split('/track/')[1].split('?')[0]
            track_info = sp.track(track_id)
            song_name = track_info['name']
            artist_name = track_info['artists'][0]['name']
            query = f"{song_name} {artist_name} Oficial"
            videosSearch = VideosSearch(query, limit=1)
            result = videosSearch.result()
            if result['result']:
                youtube_link = result['result'][0]['link']

                #Guardar el link en un archivo de texto
                with open('descargar.txt', 'a') as f:
                    f.write(youtube_link + '\n')
                    print("✔️  Video de Spotify obtenido.")
            else:
                print("❌ Ocurrió un error al obtener el video de Spotify, intente de nuevo.")

    except Exception as e:
        print(f"❌ Ocurrió un error al obtener el video de Spotify: {e}")


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
        print()
        print("↺ Obteniendo videos de la playlist de YouTube...")
        print()
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
        print()
        print("↺ Obteniendo videos de la playlist de Spotify...")
        print()
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
        print()
        if config["Descargar_video"]:
            descargar_video(url)

        if config["Descargar_audio"]:
            descargar_audio(url)

    if config["Utilizar_link_de_Spotify"]:
        print("Ingrese la url de la canción que desea descargar de Spotify:")
        url = input("-> ")
        print()
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

    print("✔️  Las descargas han finalizado.")