import discord
from dateutil.parser import parse
import os
import asyncio
from discord.ext import commands

from views.order_views import OrderView
from views.credential_views import CredentialView

class MainView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Order Check", style=discord.ButtonStyle.blurple)
    async def orderButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Select Website:", view=OrderView(bot=self.bot),ephemeral=True)

    @discord.ui.button(label="Manage Emails", style=discord.ButtonStyle.green)
    async def email_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Select Option:",view=CredentialView(bot=self.bot),ephemeral=True)
