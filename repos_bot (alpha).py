#импорт необходимых библиотек
import discord
import os
from discord.ext import commands
import pytube
from youtubesearchpython import VideosSearch
import requests
from datetime import datetime
import random
# настройка разрешений
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

song_queue = []
current = None
Giphy_token = 'wxfYvsQyjfbYUWDDJ4PEA5TSlGwSqw0f'
source = None

# префикс для команд и передача разрешений
bot = commands.Bot(command_prefix='-', intents=intents)

# проверка играет ли бот
def is_playing(ctx):
    voice_client = ctx.guild.voice_client
    return voice_client.is_playing()

# проверка на паузе ли бот
def is_paused(ctx):
    voice_client = ctx.guild.voice_client
    return voice_client.is_paused()

# проверка подключен ли бот
def is_connected(ctx):
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()

# проигрывание следующей песни
def play_next(mes):
    if len(song_queue) > 0:
        url2 = song_queue[0]
        play_song(mes, url2)
    else:
        print("конец очереди")
    

# получение ссылки на видео через запрос
def get_video_url(querry):
    video = VideosSearch(querry, limit=1)
    result = video.result()
    test = result['result'][0]['link']
    print('нашёл вот это: ' + test)
    return test

# проигрывание песни
def play_song(mes, url):
    global current
    global source
    if not ('https://www.youtube.com' in url or 'https://youtu.be' in url):
        url = get_video_url(url)

    export_path = 'C:\\pc\\python\\mp3'
    print("скачиваю...")
    yt = pytube.YouTube(url)
    print(yt.title)
    video = yt.streams.filter(only_audio=True).first()
    outfile = video.download(output_path=export_path)
    new_file = str(export_path) + "\\download.mp3"
    try: 
        os.replace(outfile, new_file)
    except:
        print("работаю...")
    source = discord.FFmpegPCMAudio(new_file)
    song_queue.pop(0)
    mes.voice_client.play(source, after=lambda e: play_next(mes))
    print(f"играет: {yt.author} ||| + {yt.title}")

    current = yt
    

# метод для генерации случайного персонажа
def generate_character():
    names = ["Алекс", "Боб", "Крис", "Дэн", "Ева", "Фрэнк", "Грейс", "Гарри"]
    classes = ["Воин", "Маг", "Лучник", "Вор"]
    characteristics = ["Сила", "Ловкость", "Интеллект", "Выносливость", "Обаяние", "Удача"]
    skills = ["Атака", "Защита", "Лечение", "Магия", "Стелс", "Торговля"]

    name = random.choice(names)
    age = random.randint(18, 60)
    char_class = random.choice(classes)

    char_stats = {char: random.randint(1, 10) for char in characteristics}
    char_skills = random.sample(skills, random.randint(1, len(skills)))

    character = {
        "Имя": name,
        "Возраст": age,
        "Класс": char_class,
        "Характеристики": char_stats,
        "Навыки": char_skills
    }

    return character

# генерация случайного персонажа
@bot.command()
async def gen_char(mes):
    char = generate_character()
    for key, value in char.items():
        await mes.send(f'{key}: {value}')

# пауза
@bot.command()
async def pause(mes):
    if is_paused(mes):
        await mes.send('я уже на паузе')
    if not is_paused(mes) and is_playing(mes):
        mes.voice_client.pause()
        await mes.send("пауза")


# пропуск
@bot.command()
async def skip(mes):
    if is_playing(mes):
        mes.voice_client.stop()
        source.cleanup()
        play_next(mes)


# продолжение воспроизведения
@bot.command()
async def resume(mes):
    if is_paused(mes):
        mes.voice_client.resume()

# добавление песни в очередь и воспроизведение
@bot.command()
async def play(mes, *, url: str):
    if( not is_connected(mes)):
        voice_state = mes.author.voice
        if (voice_state):
            await mes.send(f"захожу в : {voice_state.channel.name}")
            await voice_state.channel.connect()
        else:
            await mes.send("вы не вошли в голосовой канал")
    if (is_connected(mes)):
        song_queue.append(url)
        if (not is_playing(mes) and not is_paused(mes)):
             play_song(mes, url)

# выход из голосового канала и очищение очереди
@bot.command()
async def leave(mes):
    global song_queue
    if mes.voice_client:
        await mes.send("ухожу...")
        song_queue = []
        await mes.voice_client.disconnect()
    else:
        await mes.send('я не в голосовомм канале')

# показ очереди
@bot.command()
async def queue(mes):
    if is_connected(mes):
            if len(song_queue) > 0:
                await mes.send(f"текущая очередь: {song_queue}")
            else:
                await mes.send("очередь пуста")
    else:
        mes.send("я не в голосовом канале")

# показ информации о текущей песни
@bot.command()
async def np(mes):
    if (is_connected(mes) and is_playing(mes)):
        await mes.send(f"сейчас играет: {current.author} ||| {current.title}")
    if (is_connected(mes) and not is_playing(mes)):
        await mes.send("сейчас ничего не играет")
    if (not is_connected(mes) and not is_playing(mes)):
        await mes.send("я не в голосовом канале")

# показ случайной гифки
@bot.command()
async def randgif(mes):
    response = requests.get(f'http://api.giphy.com/v1/gifs/random?api_key={Giphy_token}&tag=&rating=pg-13')
    data = response.json()
    gif = data['data']['images']['original']['url']
    await mes.send("случайная гифка")
    await mes.send(gif)

# помощь
@bot.command()
async def helpbot(mes):
    await mes.send('Вот доступные команды: \n play - позволяет начать воспроизводить музыку из YouTube \n pause/resume - позволяет поставить на паузу и продолжить \n leave - позволяет мне выйти из голосового канала \n queue - позволяет посмотреть очередь \n skip - пропуск песни \n np - показ информации о текущей песни \n randgif - отправка случайной гифки \n findvideo - поиск 5 видео по запросу \n date - узнать текущую дату (год, месяц, день) \n gen_char - генерация случайного персонажа')

@bot.command()
async def findvideo(mes, *, text: str):
        video = VideosSearch(text, limit=5)
        result = video.result()
        await mes.send("нашёл это: ")
        for i in range(5):
            link = result['result'][i]['link']
            await mes.send(f' {i+1}: {link}')

@bot.command()
async def date(mes):
    current_time = datetime.now().strftime("%Y-%m-%d")
    await mes.send(f"сегодня: {current_time}")
bot.run('MTEzMjAzNDQxNDAyOTgzMjQxMw.GcKXFF.VT5KWlyQjdqUqjpK5s-r6mXm5itrJHOViARW_w')