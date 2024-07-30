import datetime
import discord
from discord.ext import commands

def timestamp():
    current_time = datetime.datetime.utcnow().strftime("Date = %Y-%m-%d || Time = %H:%M:%S UTC")
    return current_time

def get_channel_id(client,id_channel):
    return client.get_channel(id_channel)

