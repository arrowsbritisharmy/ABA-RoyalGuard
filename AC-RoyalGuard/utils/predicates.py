import discord
from discord.ext import commands

def is_owner_check():
    def predicate(ctx: commands.Context):
        return owner_predicate(ctx.author)
    return commands.check(predicate)
        
def owner_predicate(user: discord.User):
    if user.id in [1131274836681949254, 1021443097068044398, 1152696515882655766]:
        return True
    else:
        return False
		