import zipfile
import rarfile
import os
from pyrogram import Client, filters
from pyrogram.types import Message


CMD = ["/"]

@Client.on_message(filters.command("zip", CMD))
async def zip_files(client: Client, message: Message):
    try:
        # Extract files from the message if needed
        file_paths = message.text.split()[1:]  # Assuming files are provided in the message
        if not file_paths:
            await message.reply_text("Please provide file paths to zip.")
            return
        
        zip_filename = "archive.zip"  # Name of the output zip file
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in file_paths:
                zipf.write(file, os.path.basename(file))  # Add files to the zip

        await message.reply_text(f"Files successfully zipped into {zip_filename}")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@Client.on_message(filters.command("unzip", CMD))
async def unzip_files(client: Client, message: Message):
    try:
        zip_filename = message.text.split()[1]
        if not zip_filename.endswith(".zip"):
            await message.reply_text("Please provide a valid .zip file.")
            return

        with zipfile.ZipFile(zip_filename, 'r') as zipf:
            zipf.extractall("extracted_files")
        
        await message.reply_text(f"Files extracted to 'extracted_files' folder.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@Client.on_message(filters.command("rar", CMD))
async def rar_files(client: Client, message: Message):
    try:
        # Extract files from the message if needed
        file_paths = message.text.split()[1:]  # Assuming files are provided in the message
        if not file_paths:
            await message.reply_text("Please provide file paths to create rar.")
            return
        
        rar_filename = "archive.rar"  # Name of the output rar file
        with rarfile.RarFile(rar_filename, 'w') as rarf:
            for file in file_paths:
                rarf.add(file)  # Add files to the rar

        await message.reply_text(f"Files successfully rarred into {rar_filename}")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@Client.on_message(filters.command("unrar", CMD))
async def unrar_files(client: Client, message: Message):
    try:
        rar_filename = message.text.split()[1]
        if not rar_filename.endswith(".rar"):
            await message.reply_text("Please provide a valid .rar file.")
            return

        with rarfile.RarFile(rar_filename, 'r') as rarf:
            rarf.extractall("extracted_rar_files")

        await message.reply_text(f"Files extracted to 'extracted_rar_files' folder.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")
