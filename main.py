import discord
from discord.ext import commands
import sqlite3
import re

TOKEN = 'your_bot_token_here'

bot = commands.Bot(command_prefix='!')

# Initialize SQLite database connection
conn = sqlite3.connect('word_counts.db')
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS word_counts
             (id INTEGER PRIMARY KEY, word TEXT UNIQUE, count INTEGER)''')

# Function to fetch current count for a word
def fetch_word_count(word):
    c.execute('SELECT count FROM word_counts WHERE word = ?', (word,))
    row = c.fetchone()
    if row:
        return row[0]
    else:
        return 0

# Function to update count for a word
def update_word_count(word, count):
    c.execute('INSERT OR REPLACE INTO word_counts (word, count) VALUES (?, ?)',
              (word, count))
    conn.commit()

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Event: Message sent in any channel
@bot.event
async def on_message(message):
    content = message.content.lower()
    
    # Extract words from the message using regex
    words = re.findall(r'\b\w+\b', content)
    
    for word in words:
        # Fetch current count for the word
        current_count = fetch_word_count(word)
        
        # Increment the count
        current_count += 1
        
        # Update the count in the database
        update_word_count(word, current_count)
    
    await bot.process_commands(message)

# Command to retrieve word count with embed
@bot.command()
async def wordcount(ctx, word):
    word = word.lower()
    count = fetch_word_count(word)
    
    # Create an embed
    embed = discord.Embed(title=f'Word Count for "{word}"', color=discord.Color.blue())
    embed.add_field(name='Total Count', value=f'{count} times', inline=False)
    embed.set_footer(text=f'Requested by {ctx.author.display_name}', icon_url=ctx.author.avatar_url)
    
    await ctx.send(embed=embed)

bot.run(TOKEN)
