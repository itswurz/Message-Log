import discord
from discord.ext import commands
from discord.ui import Button, View
from discord.components import ActionRow
import os
import collections
import asyncio

# Discord bot message intent
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to store word counts
word_counts = collections.defaultdict(int)

async def update_word_counts():
    global word_counts
    print("Updating word counts...")
    word_counts = collections.defaultdict(int)
    for channel in bot.get_all_channels():
        if isinstance(channel, discord.TextChannel):
            async for message in channel.history(limit=None):
                if message.author.bot:
                    continue
                words = message.content.split()
                for word in words:
                    word_counts[word.lower()] += 1
print('Word Count Updated')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    bot.loop.create_task(update_word_counts())  # Start the background task using asyncio

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore messages from other bots

    # Update word counts
    words = message.content.split()
    for word in words:
        word_counts[word.lower()] += 1

    await bot.process_commands(message)

@bot.command(name='count')
async def count_words(ctx, page_number: int = 1):
    # Sort words by frequency (descending)
    sorted_word_counts = sorted(word_counts.items(), key=lambda item: item[1], reverse=True)

    # Number of words per page
    words_per_page = 10

    # Calculate total pages
    num_pages = (len(sorted_word_counts) + words_per_page - 1) // words_per_page

    # Validate page number
    page_number = max(1, min(page_number, num_pages))

    # Function to create an embed for the given page
    async def create_embed(page_number):
        embed = discord.Embed(title="Word Count", color=discord.Color.blue())

        # Calculate indices for the current page
        start_index = (page_number - 1) * words_per_page
        end_index = start_index + words_per_page

        # Add fields for each word and its count on the current page
        for idx, (word, count) in enumerate(sorted_word_counts[start_index:end_index], start=start_index):
            embed.add_field(name=f"{idx + 1}. {word}", value=f"Count: {count}", inline=False)

        # Add pagination buttons if needed
        components = []
        if num_pages > 1:
            if page_number > 1:
                components.append(discord.ui.Button(style=discord.ButtonStyle.primary, label="Previous", custom_id=f"count_prev"))
            if page_number < num_pages:
                components.append(discord.ui.Button(style=discord.ButtonStyle.primary, label="Next", custom_id=f"count_next"))

        action_row = discord.components.ActionRow(*components) if components else None  # Assign a value even if no buttons
        return embed, action_row
    # Send the initial embed with the specified page number
    embed, action_row = await create_embed(page_number)
    message = await ctx.send(embed=embed, components=action_row)

    # Interaction handling with buttons
    while True:
        try:
            interaction = await bot.wait_for("button_click", check=lambda inter: inter.message.id == message.id and inter.user.id == ctx.author.id, timeout=60)

            if interaction.component.custom_id == "count_prev" and page_number > 1:
                page_number -= 1
            elif interaction.component.custom_id == "count_next" and page_number < num_pages:
                page_number += 1

            # Update the embed with the new page
            embed, action_row = await create_embed(page_number)
            await interaction.respond(embed=embed, components=action_row)

        except asyncio.TimeoutError:
            await message.edit(components=None)
            break

# Replace 'YOUR_BOT_TOKEN' with your actual Discord bot token
bot.run('YOUR BOT TOKEN HERE')
