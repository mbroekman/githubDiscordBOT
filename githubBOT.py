import discord
from discord.ext import commands
import requests
import asyncio
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)

# Laad variabelen uit het .env bestand
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
FORUM_CHANNEL_ID = int(os.getenv("FORUM_CHANNEL_ID", 0))
DISCUSSION_CHANNEL_ID = int(os.getenv("DISCUSSION_CHANNEL_ID", 0))

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO_OWNER = os.getenv("GITHUB_REPO_OWNER")
GITHUB_REPO_NAME = os.getenv("GITHUB_REPO_NAME")
# GraphQL vereist het repository ID voor discussies (dit ID halen we automatisch op bij de start)
GITHUB_REPOSITORY_ID = None 

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

def get_github_repo_id():
    """Haalt het interne Node ID van de GitHub repo op, nodig voor GraphQL (Discussies)."""
    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    query = """
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        id
      }
    }
    """
    variables = {"owner": GITHUB_REPO_OWNER, "name": GITHUB_REPO_NAME}
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("repository", {}).get("id")
    return None

@bot.event
async def on_ready():
    global GITHUB_REPOSITORY_ID
    GITHUB_REPOSITORY_ID = get_github_repo_id()
    print(f"Bot successfully logged in as {bot.user}")
    print(f"Linked to GitHub Repo ID: {GITHUB_REPOSITORY_ID}")
    
    print("\n--- CHANNELS THE BOT HAS ACCESS TO ---")
    for guild in bot.guilds:
        print(f"Server: {guild.name}")
        for channel in guild.channels:
            if channel.id in [FORUM_CHANNEL_ID, DISCUSSION_CHANNEL_ID]:
                print(f"  [TARGET] {channel.name} (ID: {channel.id}) - Type: {type(channel)}")
    print("-----------------------------------------------\n")

@bot.event
async def on_message(message):
    print(f"DEBUG: Message received in channel '{message.channel}' (ID: {message.channel.id}) from {message.author}")
    await bot.process_commands(message)

async def get_first_message(thread):
    """Hulpfunctie om het allereerste bericht uit een thread op te halen."""
    await asyncio.sleep(2) # Wacht kort tot Discord het bericht heeft verwerkt
    async for message in thread.history(limit=1, oldest_first=True):
        return message
    return None

async def create_github_issue(thread, title, body):
    """Maakt een traditioneel Issue aan via de REST API."""
    url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/issues"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    payload = {"title": f"[Issue] {title}", "body": body}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        return response.json().get("html_url")
    return None

async def create_github_discussion(thread, title, body):
    """Maakt een Discussie aan via de GitHub GraphQL API."""
    # Tip: Je moet 'Discussions' hebben ingeschakeld in je GitHub Repo instellingen!
    # We gebruiken hier de algemene categorie (je kunt eventueel een specifiek categoryId opgeven)
    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    
    # Eerst halen we de categorieën op om de eerste bruikbare te pakken
    cat_query = """
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        discussionCategories(first: 1) {
          nodes { id }
        }
      }
    }
    """
    cat_res = requests.post(url, json={"query": cat_query, "variables": {"owner": GITHUB_REPO_OWNER, "name": GITHUB_REPO_NAME}}, headers=headers)
    try:
        category_id = cat_res.json()["data"]["repository"]["discussionCategories"]["nodes"][0]["id"]
    except Exception:
        return None

    mutation = """
    mutation($repoId: ID!, $catId: ID!, $title: String!, $body: String!) {
      createDiscussion(input: {repositoryId: $repoId, categoryId: $catId, title: $title, body: $body}) {
        discussion {
          url
        }
      }
    }
    """
    variables = {
        "repoId": GITHUB_REPOSITORY_ID,
        "catId": category_id,
        "title": f"[Discussion] {title}",
        "body": body
    }
    response = requests.post(url, json={"query": mutation, "variables": variables}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("createDiscussion", {}).get("discussion", {}).get("url")
    return None

@bot.event
async def on_thread_create(thread):
    print(f"DEBUG: New thread detected: '{thread.name}' (ID: {thread.id})")
    print(f"DEBUG: Parent channel ID: {thread.parent_id}")
    print(f"DEBUG: Expected channels: FORUM={FORUM_CHANNEL_ID}, DISCUSSION={DISCUSSION_CHANNEL_ID}")

    # Controleer of het om een van onze geselecteerde kanalen gaat
    if thread.parent_id not in [FORUM_CHANNEL_ID, DISCUSSION_CHANNEL_ID]:
        print(f"DEBUG: Thread ignored, parent_id does not match.")
        return

    print("DEBUG: Thread matches target channels, fetching first message...")

    first_message = await get_first_message(thread)
    content = first_message.content if first_message else "No description provided."
    author = first_message.author.name if first_message else "Unknown"
    
    body_text = f"**Submitted from Discord by:** {author}\n\n**Content:**\n{content}"

    if thread.parent_id == FORUM_CHANNEL_ID:
        # Actie voor het Suggesties Forum -> Issue
        url = await create_github_issue(thread, thread.name, body_text)
        type_name = "issue"
    elif thread.parent_id == DISCUSSION_CHANNEL_ID:
        # Actie voor het Discussie Kanaal -> GitHub Discussion
        url = await create_github_discussion(thread, thread.name, body_text)
        type_name = "discussion"

    if url:
        await thread.send(f"✅ This {type_name} has been successfully forwarded to GitHub! View it here: {url}")
    else:
        await thread.send(f"⚠️ Something went wrong while creating the {type_name} on GitHub.")

bot.run(DISCORD_TOKEN)
