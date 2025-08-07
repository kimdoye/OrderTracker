import discord 
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Select

# Import the database functions that the UI components need
from utils.database_handler import set_user_credential, delete_user_credential,get_all_user_emails

class CredentialsModal(Modal, title="Set Email Credentials"):
    """A Modal for inputting email and password."""
    email = TextInput(label="Email Address", placeholder="your.email@example.com", required=True)
    password = TextInput(label="IMAP Password", required=True)

    def __init__(self, db):
        super().__init__()
        self.db = db

    async def on_submit(self, interaction: discord.Interaction):
        await set_user_credential(self.db, interaction.user.id, self.email.value, self.password.value)
        await interaction.response.send_message(f"✅ Your credentials for **{self.email.value}** have been saved.", ephemeral=True)


class DeleteSelectView(View):
    """A View containing a dropdown of email addresses to delete."""
    def __init__(self, db, accounts: list):
        super().__init__(timeout=180)
        self.db = db
        
        options = [discord.SelectOption(label=acc[0]) for acc in accounts]
        self.select_menu = Select(placeholder="Choose an email account to delete...", options=options)
        
        # Define the callback function for the select menu
        async def select_callback(interaction: discord.Interaction):
            email_to_delete = self.select_menu.values[0]
            await delete_user_credential(self.db, interaction.user.id, email_to_delete)
            await interaction.response.edit_message(content=f"✅ Successfully deleted credentials for **{email_to_delete}**.", view=None, ephemeral=True)

        self.select_menu.callback = select_callback
        self.add_item(self.select_menu)

class CredentialView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot


    @discord.ui.button(label="Add Account", style=discord.ButtonStyle.blurple)
    async def addButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CredentialsModal(db=self.bot.db))

    @discord.ui.button(label="Delete Account", style=discord.ButtonStyle.blurple)
    async def delButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        accounts = await get_all_user_emails(self.bot.db, interaction.user.id)
        if not accounts:
            await interaction.response.edit_message("You have no credentials stored to delete.", ephemeral=True)
            return
        await interaction.response.edit_message(content="Select Account to Delete:", view=DeleteSelectView(db=self.bot.db,accounts=accounts))

    @discord.ui.button(label="View Accounts", style=discord.ButtonStyle.blurple)
    async def viewButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        creds = await get_all_user_emails(self.bot.db, interaction.user.id)
        if not creds:
            await interaction.response.send_message("You have no credentials stored.", ephemeral=True)
            return

        email_list = "\n".join([f"- 📧 {email[0]}" for email in creds])
        embed = discord.Embed(
            title="Your Stored Email Accounts",
            description=email_list,
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


