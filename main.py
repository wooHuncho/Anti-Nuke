import discord, pymongo, requests, json
from discord.ext import commands



bot = commands.Bot(command_prefix="?", intents=discord.Intents.all())
bot.remove_command("help")
bot.load_extension("jishaku")
with open("config.json", "r") as f:
    s = json.load(f)
    token = s['Token']
    url = s['URL']
client = pymongo.MongoClient(url)
welc = client["anti"]["welcome"]
anti = client["anti"]["anti"]
mod = client["anti"]["mod"]
ui = client["anti"]["userinfo"]


headers = {
    "Authorization": f"Bot {token}"
}

class OnReady:
    @bot.event
    async def on_ready():
        print(f"Connected: {bot.user}")
        print(f"ID: {bot.user.id}")



    

class MessageEvent:
    @bot.event
    async def on_message(message):
        if "discord.gg/" in message.content:
            if message.author.id in anti.find_one({"_id": message.guild.id})["whitelisted"]:
                return
            else:
                chan = anti.find_one({"_id": message.guild.id})["modlogs-id"]
                channel = bot.get_channel(chan)
                if channel is None:
                    return
                else:
                    embed = discord.Embed(title="Mod-Logs | Invite Deleted", timestamp = message.created_at, color=discord.Color.from_rgb(255,250,250), description="Invite Message Deleted!")
                    embed.add_field(name=f"Author", value=message.author)
                    embed.add_field(name=f"Content", value=message.content)
                    await channel.send(embed=embed)
                await message.delete()
                await message.channel.send(f"{message.author.mention} please don't send discord server invites",delete_after=5)
        l = welc.find_one({"_id": message.guild.id})
        if l is None:
            welc.insert_one({"_id": message.guild.id,
           "events": True,
           "message": None,
           "embed": True,
           "footer": None,
           "title": None,
           "channel": None})
            anti.insert_one({"_id": message.guild.id,
           "anti-ban": True,
           "anti-raid": False,
           "anti-channel": True,
           "anti-kick": True,
           "anti-webhook": True,
           "modlogs-id": None,
           "anti-role": True,
           "anti-update": True,
           "whitelisted": []
           })
            mod.insert_one({"_id": message.guild.id,
            "mute_role": None,
            "punishment": "ban"})

        await bot.process_commands(message)

class AntiNuke:

    @bot.command()
    async def whitelist(ctx, member:discord.Member):
        if ctx.author == ctx.guild.owner:
             try:
              anti.update_one({"_id": ctx.guild.id},
            {"$push": {"whitelisted": member.id}})
              await ctx.reply(f"{member} has been added to the whitelisted users!")
             except:
              await ctx.reply(f"Failed to add {member} to the whitelisted users!")
        else:
            embed = discord.Embed(title="Error | Not Owner",description="This command requires you to be the **Guild Owner**!",color=discord.Color.from_rgb(255, 0 ,0 ))
            await ctx.reply(embed=embed,delete_after=20)
        
    @bot.command()
    async def whitelisted(ctx):
        embed = discord.Embed(title="Whitelisted Users", color=discord.Color.from_rgb(255,250,250), description="")
        embed.set_footer(text=f"Requested by: {ctx.author.name}",icon_url=ctx.guild.icon_url)
        if ctx.author == ctx.guild.owner:
            for member in anti.find_one({"_id": ctx.guild.id})["whitelisted"]:
                mem = bot.get_user(member)
                embed.description += f"{mem}`({mem.id})`\n"
            await ctx.reply(embed=embed)
        
        else:
         embed = discord.Embed(title="Error | Not Owner",description="This command requires you to be the **Guild Owner**!",color=discord.Color.from_rgb(255, 0 ,0 ))
         await ctx.reply(embed=embed,delete_after=20)

    @bot.command()
    async def unwhitelist(ctx, member:discord.Member):
        if ctx.author == ctx.guild.owner:
         if member not in anti.find_one({"_id": ctx.guild.id})["whitelisted"]:
             embed = discord.Embed(color=discord.Color.from_rgb(255, 0 ,0 ), title = "Error | Member Not Whitelisted",description=f"{member} is not whitelisted!")
             await ctx.reply(embed=embed)
         else:
              anti.update_one({"_id": ctx.author.id},
             {"$pull": {"whitelisted": member.id}})
              embed = discord.Embed(timestamp=ctx.message.created_at, title="Member Unwhitelisted", color=discord.Color.from_rgb(0, 255, 0 ), description=f"{member} has been unwhitelisted!")
              await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(title="Error | Not Owner",description="This command requires you to be the **Guild Owner**!",color=discord.Color.from_rgb(255, 0 ,0 ))
            await ctx.reply(embed=embed,delete_after=20)

        
class Config:

    @bot.group(invoke_without_command=True)
    async def config(ctx):
        "s"

    @config.command()
    async def modlogs(ctx, channel: discord.TextChannel):
        if ctx.author == ctx.guild.owner:
            try:
                anti.update_one({"_id": ctx.guild.id},
                {"$set": {"modlogs-id": channel.id}})
                embed = discord.Embed(color=discord.Color.from_rgb(0 ,255, 0 ), title = "Mod-Logs Set", description=f"{channel.mention} is the new Mod-Logs channel!")
                await ctx.reply(embed=embed)
            except:
                embed = discord.Embed(color = discord.Color.from_rgb(255, 0 ,0 ), title = "Error | Failed", description=f"{channel.mention} could not be set")
                await ctx.reply(embed = embed)
        else:
            embed = discord.Embed(title="Error | Not Owner",description="This command requires you to be the **Guild Owner**!",color=discord.Color.from_rgb(255, 0 ,0 ))
            await ctx.reply(embed=embed,delete_after=20)


    @config.group(invoke_without_command=True)
    async def welcome(ctx):
        "s"

    @welcome.command(aliases=["message"])
    async def msg(ctx, *, message):
        if ctx.author is ctx.guild.owner:
            try:
                welc.update_one({"_id": ctx.guild.id},
                {"$set": {"message": message}})
                embed = discord.Embed(title="Welcome Message Updated | Database Updated",color=discord.Color.from_rgb(0, 255, 0 ), description="Your welcome message has been updated\n`?settings` to see your servers current settings")
                await ctx.reply(embed=embed)
            except:
                embed = discord.Embed(title="Error | Failed",color=discord.Color.from_rgb(255, 0 ,0 ),description="Failed to set Welcome Message")
                await ctx.reply(embed=embed)
        else:
           embed = discord.Embed(title="Error | Not Owner",description="This command requires you to be the **Guild Owner**!",color=discord.Color.from_rgb(255, 0 ,0 ))
           await ctx.reply(embed=embed,delete_after=20) 


class Settings:
    "because it deserves its own clas :)"
    @bot.command()
    async def settings(ctx):
     if ctx.author is ctx.guild.owner:
         msg = welc.find_one({"_id": ctx.guild.id})["message"]
         chan = welc.find_one({'_id': ctx.guild.id})["channel"]
         channel = bot.get_channel(chan)
         events = welc.find_one({"_id": ctx.guild.id})['events']
         ban = anti.find_one({"_id": ctx.guild.id})['anti-ban']
         embed = discord.Embed(title=f"Settings | {ctx.guild}",color=discord.Color.from_rgb(255,250,250), description="To change any of this simply do\n`?config`")
         embed.add_field(name="Welcome",value=f"> Events: `{events}`\n> Message: `{msg}`\n> Channel: `{channel}`")
         embed.add_field(name="Anti-Nuke",value=f"> Anti-Ban: `{ban}`")
         embed.add_field(name=f"Prefix",value="> ?")
         await ctx.reply(embed=embed)
     else:
        embed = discord.Embed(title="Error | Not Owner",description="This command requires you to be the **Guild Owner**!",color=discord.Color.from_rgb(255, 0 ,0 ))
        await ctx.reply(embed=embed,delete_after=20) 

@bot.event
async def on_guild_join(guild):
     welc.insert_one({"_id": guild.id,
           "events": True,
           "message": None,
           "embed": True,
           "footer": None,
           "title": None,
           "channel": None}),
     anti.insert_one({"_id": guild.id,
           "anti-ban": True,
           "anti-raid": False,
           "anti-channel": True,
           "anti-kick": True,
           "anti-webhook": True,
           "modlogs-id": None,
           "anti-role": True,
           "anti-update": True,
           "whitelisted": []
           })
     mod.insert_one({"_id": guild.id,
            "mute_role": None,
            "punishment": "ban"})
@bot.command()
async def db(ctx):
    if ctx.author.id == 911626804983377991:
        for guild in bot.guilds:
           welc.insert_one({"_id": ctx.guild.id,
           "events": True,
           "message": None,
           "embed": True,
           "footer": None,
           "title": None,
           "channel": None}),
           anti.insert_one({"_id": ctx.guild.id,
           "anti-ban": True,
           "anti-raid": False,
           "anti-channel": True,
           "anti-kick": True,
           "anti-webhook": True,
           "modlogs-id": None,
           "anti-role": True,
           "anti-update": True,
           "whitelisted": []
           })
           mod.insert_one({"_id": ctx.guild.id,
            "mute_role": None,
            "punishment": "ban"})

    else:
        return

class Moderation:

    @bot.command()
    @commands.has_permissions(ban_members=True)
    async def ban(ctx, member: discord.Member, *, reason = None):
        if member.top_role > ctx.author.top_role:
            embed = discord.Embed(title="Error | Member has Higher Role",description=f"{member} has a higher top role than you.",color=discord.Color.from_rgb(255, 0, 0 ))
            await ctx.reply(embed=embed)
        elif member.top_role > bot.user.top_role:
            embed = discord.Embed(title="Error | Bot Role too Low", description=f"I need a higher role than {member.name}`s role in order to ban them.", color=discord.Color.from_rgb(255, 0, 0))
            await ctx.reply(embed = embed)
        else:
            try:
                await member.ban(reason=reason)
                await ctx.reply(f"{member} has been banned")
                await member.send(f"You have been banned from {ctx.guild}\nReason: {reason}")
            except:
                await ctx.reply(f"An unexpected error occurred!\nFailed to ban {member}")
    
    @bot.command()
    @commands.has_permissions(kick_members=True)
    async def kick(ctx, member: discord.Member, *, reason = None):
        if member.top_role > ctx.author.top_role:
            embed = discord.Embed(title="Error | Member has Higher Role",description=f"{member} has a higher top role than you.",color=discord.Color.from_rgb(255, 0, 0 ))
            await ctx.reply(embed=embed)
        elif member.top_role > bot.user.top_role:
            embed = discord.Embed(title="Error | Bot Role too Low", description=f"I need a higher role than {member.name}`s role in order to ban them.", color=discord.Color.from_rgb(255, 0, 0))
            await ctx.reply(embed = embed)
        elif member is ctx.author:
            return
        elif member is bot.user: return
        else:
            try:
                await member.kick(reason=reason)
                await ctx.reply(f"{member} has been kicked")
                await member.send(f"You have been kicked from {ctx.guild}\nReason: {reason}")
            except:
                await ctx.reply(f"An unexpected error occurred!\nFailed to kick {member}")
        
        

bot.run(token)