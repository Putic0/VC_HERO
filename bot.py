import discord
from discord.ext import commands
import asyncio
import os

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


@bot.command(name="join", aliases=["connect"])
async def join(ctx):
    if ctx.author.voice is None:
        return await ctx.send("❌ You need to be in a voice channel first.")

    channel = ctx.author.voice.channel

    if ctx.voice_client is not None:
        await ctx.voice_client.move_to(channel)
        await ctx.send(f"🔄 Moved to **{channel.name}**")
    else:
        await channel.connect()
        def play_audio(error):
    if ctx.voice_client and ctx.voice_client.is_connected():
        import time
        time.sleep(5)
        source = discord.FFmpegPCMAudio('ambatu.mp3')
        ctx.voice_client.play(source, after=play_audio)

source = discord.FFmpegPCMAudio('ambatu.mp3')
ctx.voice_client.play(source, after=play_audio)
        await ctx.send(f"🎙️ Joined **{channel.name}** — I'll stay even if I'm alone.")
        await bot.change_presence(activity=discord.Game(name=f"Saving {channel.name}"))

@bot.command(name="leave", aliases=["disconnect", "dc"])
async def leave(ctx):
    if ctx.voice_client is None:
        return await ctx.send("❌ I'm not in any voice channel.")

    global intentional_disconnect
    intentional_disconnect = True
    channel_name = ctx.voice_client.channel.name
    await ctx.voice_client.disconnect()
    await ctx.send(f"👋 Left **{channel_name}**.")
    await ctx.send(f"I leave the vc to you now...! https://tenor.com/view/spider-man-edit-funk-raphyx-spiderman-gif-1582522054178700448")
    await bot.change_presence(activity=None)


@bot.command(name="move")
async def move(ctx, *, channel_name: str):
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
    voice_channels = [c for c in ctx.guild.channels if isinstance(c, discord.VoiceChannel)]
    if not voice_channels:
        return await ctx.send("❌ No voice channels found in this server.")

    listing = "\n".join(f"• `{c.name}` ({len(c.members)} connected)" for c in voice_channels)
    await ctx.send(f"📋 **Available voice channels:**\n{listing}")


@bot.event
async def on_voice_state_update(member, before, after):
    global intentional_disconnect

    if member.id != bot.user.id:
        return

    if intentional_disconnect:
        intentional_disconnect = False
        return

    if before.channel is not None and after.channel is None:
        print(f"⚠️  Bot disconnected from '{before.channel.name}', attempting to reconnect...")
        await asyncio.sleep(3)
        try:
            await before.channel.connect()
            print(f"✅ Reconnected to '{before.channel.name}'")
        except Exception as e:
            print(f"❌ Could not reconnect: {e}")
            await bot.change_presence(activity=None)


if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERROR: DISCORD_TOKEN not found in .env file")
        print("   Create a .env file with: DISCORD_TOKEN=your_token_here")
    else:
        bot.run(TOKEN)
