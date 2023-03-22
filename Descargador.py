import moviepy.editor as mp
from platform import system
from pytube import YouTube
from time import sleep
from art import *
import shutil
import json
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
        "Utilizar_canciones.txt": False,
        "Utilizar_una_carpeta": False,
        "Utilizarffmpeg": True
    }
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

    limpiar_pantalla()
    tprint("YouTube - Downloader")
    print("Developed by Fvitu")
    print("------------------------------------------------------------------------------------------\n")
    sleep(2)
    limpiar_pantalla()

    print("Bienvenido, aquí podrá descargar videos o audios de YouTube totalmente gratis y de manera sencilla. Solo tendrá que configurar el archivo llamado 'config.json' para poder utilizar esta aplicación. Gracias")

    if not os.path.exists("canciones.txt"):
        with open("canciones.txt", 'w') as f:
            f.write("Si quieres puedes utilizar este archivo para descargar videos/canciones masivamente. Solo tienes que eliminar esta linea y agregar las url's una debajo de la otra.")
            f.close()

    exit()

#------------------------------#


if not os.path.exists("canciones.txt"):
    with open("canciones.txt", 'w') as f:
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


def descargar_audio(url):
    try:
        yt = YouTube(url)
        titulo = yt.title
        print(f"🡳  Descargando audio de: '{titulo}'...")
        stream = yt.streams.filter(only_audio=True).first()
        stream.download()

        if config["Utilizarffmpeg"]:
            mp4_file = stream.default_filename

            mp3_file = mp4_file.replace('.mp4', '.mp3')
            clip = mp.AudioFileClip(mp4_file)
            clip.write_audiofile(mp3_file)

            os.remove(mp4_file)

            if config["Utilizar_una_carpeta"]:
                mover_a_canciones(os.path.basename(mp3_file))
            else:
                mover_a_carpeta(os.path.basename(mp3_file), "Audio")

        else:
            mover_a_canciones(stream.default_filename)

        print(f"✔️  Se ha descargado '{titulo}' con éxito.\n")

    except:
        print("❌ Ocurrió un error al descargar el archivo, intente de nuevo.")
        exit()

#------------------------------#


def descargar_video(url=False):
    try:
        yt = YouTube(url)
        titulo = yt.title
        print(f"🡳  Descargando video  de: '{titulo}'...")
        stream = yt.streams.get_highest_resolution()
        stream.download()

        if config["Utilizar_una_carpeta"]:
            mover_a_canciones(stream.default_filename)
        else:
            mover_a_carpeta(stream.default_filename, "Video")

        print(f"✔️  Se ha descargado '{titulo}' con éxito.\n")

    except:
        print("❌ Ocurrió un error al descargar el archivo, intente de nuevo.")
        exit()

#------------------------------#


if __name__ == '__main__':
    limpiar_pantalla()
    tprint("YouTube - Downloader")
    print("Developed by Fvitu")
    print("------------------------------------------------------------------------------------------\n")
    sleep(2)
    limpiar_pantalla()

    if config["Utilizar_canciones.txt"]:
        if os.path.getsize("canciones.txt") == 0:
            print("Antes de descargar alguna canción, debe de ingresar la url del video que desea descargar en el archivo 'canciones.txt'. \n")

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

    if not config["Utilizar_canciones.txt"]:
        print("Ingrese la url del video/canción que desea descargar:")
        url = str(input("-> "))
        print("")
        if config["Descargar_video"]:
            descargar_video(url)

        if config["Descargar_audio"]:
            descargar_audio(url)
