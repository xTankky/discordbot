import discord

async def Success(ctx, text):
    embed = discord.Embed(title="Success    ✅", color=0x00FF00, description=text)
    await ctx.send(embed=embed)

async def Fail(ctx, text):
    title = "Fail"
    embed = discord.Embed(title="Fail   ❌", color=0xFF0000, description=text)
    await ctx.send(embed=embed)