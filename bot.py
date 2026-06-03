import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
intentional_disconnect = False

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Bot connected as: {bot.user}")
    print(f"🔗 In {len(bot.guilds)} server(s)")
    try:
        synced = await bot.tree.sync()
        print(f"⚙️  {len(synced)} slash commands synced")
    except Exception as e:
        print(f"Error syncing commands: {e}")


# ─── Prefix Commands (!join, !leave, etc.) ──────────────────────────────────

@bot.command(name="join", aliases=["connect"])
async def join(ctx):
    """Join the voice channel the user is in."""
    if ctx.author.voice is None:
        return await ctx.send("❌ You need to be in a voice channel first.")

    channel = ctx.author.voice.channel

    if ctx.voice_client is not None:
        await ctx.voice_client.move_to(channel)
        await ctx.send(f"🔄 Moved to **{channel.name}**")
    else:
        await channel.connect()
        await ctx.send(f"🎙️ Joined **{channel.name}** — I'll stay even if I'm alone.")


@bot.command(name="leave", aliases=["disconnect", "dc"])
async def leave(ctx):
    """Disconnect the bot from the voice channel."""
    if ctx.voice_client is None:
        return await ctx.send("❌ I'm not in any voice channel.")

    channel_name = ctx.voice_client.channel.name
    global intentional_disconnect
    intentional_disconnect = True
    await ctx.voice_client.disconnect()
    await ctx.send(f"👋 Left **{channel_name}**.")



@bot.command(name="move")
async def move(ctx, *, channel_name: str):
    """Move the bot to another voice channel by name."""
    if ctx.voice_client is None:
        return await ctx.send("❌ I'm not in a voice channel. Use `!join` first.")

    channel = discord.utils.find(
        lambda c: c.name.lower() == channel_name.lower() and isinstance(c, discord.VoiceChannel),
        ctx.guild.channels
    )

    if channel is None:
        return await ctx.send(f"❌ Couldn't find a voice channel named `{channel_name}`.")

    await ctx.voice_client.move_to(channel)
    await ctx.send(f"🔄 Moved to **{channel.name}**.")


@bot.command(name="status")
async def status(ctx):
    """Show whether the bot is in a voice channel."""
    if ctx.voice_client and ctx.voice_client.is_connected():
        channel = ctx.voice_client.channel
        members = [m for m in channel.members if not m.bot]
        await ctx.send(
            f"🟢 Currently in **{channel.name}** "
            f"({'with ' + str(len(members)) + ' member(s)' if members else 'alone'}). "
            f"I'll stay even if nobody is here."
        )
    else:
        await ctx.send("🔴 Not connected to any voice channel.")


@bot.command(name="channels")
async def channels(ctx):
    """List all voice channels in the server."""
    voice_channels = [c for c in ctx.guild.channels if isinstance(c, discord.VoiceChannel)]
    if not voice_channels:
        return await ctx.send("❌ No voice channels found in this server.")

    listing = "\n".join(f"• `{c.name}` ({len(c.members)} connected)" for c in voice_channels)
    await ctx.send(f"📋 **Available voice channels:**\n{listing}")



# ─── Auto-reconnect if Discord disconnects the bot ──────────────────────────

@bot.event
async def on_voice_state_update(member, before, after):
    """
    If the bot gets unexpectedly disconnected (Discord timeout),
    attempt to reconnect to the channel it was in.
    """
    global intentional_disconnect
    if intentional_disconnect:
    intentional_disconnect = False
    return

    if member.id != bot.user.id:
        return  # Only care about the bot's own state
        global intentional_disconnect
    if intentional_disconnect:
        intentional_disconnect = False
    return

    # Bot was disconnected (had a channel before, has none now)
    if before.channel is not None and after.channel is None:
        print(f"⚠️  Bot disconnected from '{before.channel.name}', attempting to reconnect...")
        await asyncio.sleep(3)
        try:
            await before.channel.connect()
            print(f"✅ Reconnected to '{before.channel.name}'")
        except Exception as e:
            print(f"❌ Could not reconnect: {e}")


if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERROR: DISCORD_TOKEN not found in .env file")
        print("   Create a .env file with: DISCORD_TOKEN=your_token_here")
    else:
        bot.run(TOKEN)
