import asyncio

file_queue = asyncio.Queue()

def get_queue():
    return file_queue