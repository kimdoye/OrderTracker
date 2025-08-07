import discord
from discord.ext import commands

# Import the main view from our new views file
from views.main_views import MainView

class StartCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="start")
    async def start_command(self, ctx: commands.Context):
        """Deletes the user's command and displays the main interaction view."""
        await ctx.message.delete()
        
        # Create an instance of the view, passing the bot object to it
        view = MainView(bot=self.bot)
        await ctx.send("Please select an option:", view=view)

    @commands.command(name="nuke", aliases=["resetchannel"])
    async def nuke_command(self, ctx: commands.Context):
        """Clones and replaces a channel, effectively deleting all messages."""
        
        original_channel = ctx.channel
        
        # Store properties of the channel to be nuked
        channel_properties = {
            'name': original_channel.name,
            'category': original_channel.category,
            'position': original_channel.position,
            'topic': original_channel.topic,
            'slowmode_delay': original_channel.slowmode_delay,
            'nsfw': original_channel.nsfw,
            'overwrites': original_channel.overwrites
        }
        
        # Delete the original channel
        await original_channel.delete(reason=f"Nuked by {ctx.author}")
        
        # Create a new channel with the stored properties
        new_channel = await ctx.guild.create_text_channel(**channel_properties, reason=f"Nuked by {ctx.author}")
        
        # Send a confirmation GIF/message in the new channel
        embed = discord.Embed(
            title="Channel Nuked!",
            description=f"This channel has been successfully reset by {ctx.author.mention}.",
            color=discord.Color.red()
        )
        embed.set_image(url="https://media.giphy.com/media/oe33xf3B50fsc/giphy.gif")
        await new_channel.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(StartCog(bot))