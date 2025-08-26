import discord
from discord.ui import Modal, TextInput, View, Select
from dateutil.parser import parse
import os
import asyncio
from discord.ext import commands
import datetime

# We import our new utility function
from utils.email_handler import search_emails
# We need the function to get the user's stored credentials
from utils.database_handler import get_all_user_credentials

# Your DateInputModal class remains unchanged.
class DateInputModal(Modal, title="Enter a Date Range"):
    startInputValue = TextInput(label="Scrap Date", placeholder="YYYYMMDD or Y or T", required=True)

    def __init__(self, future: asyncio.Future):
        super().__init__(timeout=300)
        self.future = future

    async def on_submit(self, interaction: discord.Interaction):
        startInput = self.startInputValue.value
        try:
            if startInput.lower() == 't':
                # If so, use datetime to get the current date.
                start_date_dt = datetime.date.today()
            elif startInput.lower() == 'y':
                # Yesterday 
                 start_date_dt = datetime.date.today() - datetime.timedelta(days=1)
            else:
                # 2. Otherwise, fall back to parsing the input as a normal date.
                start_date_dt = parse(startInput).date()
            
            result_data = {
                "start_date": start_date_dt,
                "interaction": interaction,
            }
            self.future.set_result(result_data)
        except ValueError:
            self.future.set_exception(ValueError("Invalid date format."))
            await interaction.response.send_message("❌ **Error:** Invalid date format. Please use `YYYYMMDD`.", ephemeral=True)

    async def on_timeout(self):
        if not self.future.done():
            self.future.set_exception(asyncio.TimeoutError("Modal timed out."))

class AccountSelectView(View):
    def __init__(self, bot: commands.Bot, user_credentials: list, search_params: dict):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_credentials = user_credentials
        self.search_params = search_params

        # Create the dropdown options from the fetched credentials
        options = [discord.SelectOption(label=email, description="Use this email account") for email, password in user_credentials]
        self.add_item(self.AccountSelect(options=options, placeholder="Choose an email account..."))

    class AccountSelect(Select):
        async def callback(self, interaction: discord.Interaction):
            # 'self.view' gives us access to the parent AccountSelectView's attributes
            selected_email = self.values[0]

            # Find the credentials that match the selected email
            username, password = next((email, pwd) for email, pwd in self.view.user_credentials if email == selected_email)
            self.view.clear_items()

            # Now, trigger the date modal, reusing the future pattern
            try:
                future = self.view.bot.loop.create_future()
                await interaction.response.send_modal(DateInputModal(future))
                result = await asyncio.wait_for(future, timeout=300)

                modal_interaction = result["interaction"]
                start_date = result["start_date"]

                await modal_interaction.response.defer(ephemeral=True, thinking=True)


                # Use the credentials and parameters passed to this view
                placed_result = search_emails(
                    username=username,
                    password=password,
                    subject=self.view.search_params["subject"],
                    sender=self.view.search_params["sender"],
                    start_date_dt=start_date,
                    end_date_dt=start_date
                )
                canceled_result = search_emails(
                    username=username, password=password,
                    subject=self.view.search_params["subject_canceled"],
                    sender=self.view.search_params["sender"],
                    start_date_dt=start_date, end_date_dt=start_date
                    )

                embed = discord.Embed(
                    title=f"{self.view.search_params['retailer']} Orders",
                    description=f"Scraped: `{username}`",
                    color=discord.Color.blue()
                )
                embed.add_field(name="✅ Placed Orders", value=str(placed_result), inline=True)
                embed.add_field(name="❌ Canceled Orders", value=str(canceled_result), inline=True)
                embed.add_field(name="🗓️ Date Scraped", value=f"{start_date}", inline=False)
                embed.set_footer(text="Order Tracker")
                embed.timestamp = discord.utils.utcnow()

                await modal_interaction.followup.send(embed=embed)


            except asyncio.TimeoutError:
                await modal_interaction.followup.send(content="❌ You took too long to respond.", embed=None, view=None)
            except ValueError as e:
                print(f"Validation Error: {e}")
            except Exception as e:
                await modal_interaction.followup.send(content=f"An unexpected error occurred: {e}", embed=None, view=None)


class OrderView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    async def _handle_order_check(self, interaction: discord.Interaction, search_params: dict):
        """A helper function to handle the logic for any retailer button."""
        user_creds = await get_all_user_credentials(self.bot.db, interaction.user.id)

        # 2. Check if the user has any accounts stored
        if not user_creds:
            await interaction.response.edit_message(
                content="❌ You have no email accounts stored. Please add one first.",
                view=None
            )
            return
        
        # 3. Send the new AccountSelectView
        # This view is temporary and will guide the user through the next steps.
        await interaction.response.edit_message(
            content=f"Please select an account to search for **{search_params['retailer']}** orders.",
            view=AccountSelectView(self.bot, user_creds, search_params),
        )

    @discord.ui.button(label="Best Buy", style=discord.ButtonStyle.blurple)
    async def bbButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        # The button now just defines its parameters and calls the handler
        best_buy_params = {
            "retailer": "Best Buy",
            "sender": "bestbuyinfo@emailinfo.bestbuy.com",
            "subject": "Thanks for your order",
            "subject_canceled": "Your Best Buy order has been canceled."
        }
        await self._handle_order_check(interaction, best_buy_params)

    @discord.ui.button(label="Walmart", style=discord.ButtonStyle.green)
    async def wmButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        walmart_params = {
            "retailer": "Walmart",
            "sender": "help@walmart.com",
            "subject": ", thanks for your order",
            "subject_canceled": "Canceled: delivery from order #"

        }
        await self._handle_order_check(interaction, walmart_params)