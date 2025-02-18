import discord
import config_discordbot as cfg
from helpers import pagination

from gamestonk_terminal.stocks.dark_pool_shorts import stockgrid_model


async def pos_command(ctx, arg="dpp_dollar", arg2="10"):
    try:
        # Debug
        if cfg.DEBUG:
            print(f"!stocks.dps.pos {arg} {arg2}")

        # Help
        if arg == "-h" or arg == "help":
            dark_pool_sort = {
                "sv": "Short Vol. (1M)",
                "sv_pct": "Short Vol. %",
                "nsv": "Net Short Vol. (1M)",
                "nsv_dollar": "Net Short Vol. ($100M)",
                "dpp": "DP Position (1M)",
                "dpp_dollar": "DP Position ($1B)",
            }

            help_txt = "Get dark pool short positions. [Source: Stockgrid]\n"

            possible_args = ""
            for k, v in dark_pool_sort.items():
                possible_args += f"\n{k}: {v}"

            help_txt += "\nPossible arguments:\n"
            help_txt += "<SORT> Field for which to sort by. Default: dpp_dollar\n"
            help_txt += f"The choices are:{possible_args}\n"
            help_txt += "<NUM> Number of top tickers to show. Default: 10"

            embed = discord.Embed(
                title="Stocks: [Stockgrid] Dark Pool Short Position HELP",
                description=help_txt,
                colour=cfg.COLOR,
            )
            embed.set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )

            await ctx.send(embed=embed)

        else:
            # Parse argument
            sort = arg

            try:
                num = int(arg2)
                if num < 0:
                    raise ValueError("Number has to be above 0")
            except ValueError:
                title = "ERROR Stocks: [Stockgrid] Dark Pool Short Position"
                embed = discord.Embed(title=title, colour=cfg.COLOR)
                embed.set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
                embed.set_description(
                    "No number (int) entered in the second argument."
                    "\nEnter a valid (positive) number, example: 10"
                )
                await ctx.send(embed=embed)
                if cfg.DEBUG:
                    print("ERROR: No (positive) int for second argument entered")
                return

            try:
                df = stockgrid_model.get_dark_pool_short_positions(sort, False)
            except Exception as e:
                title = "ERROR Stocks: [Stockgrid] Dark Pool Short Position"
                embed = discord.Embed(title=title, colour=cfg.COLOR)
                embed.set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
                embed.set_description(
                    f"Sorting parameter given: {arg}"
                    "\nEnter a valid ticker, example: dpp_value"
                )
                await ctx.send(embed=embed)
                if cfg.DEBUG:
                    print(f"POSSIBLE ERROR: Wrong sort parameter entered\n{e}")
                return

            df = df.iloc[:num]
            dp_date = df["Date"].values[0]
            df = df.drop(columns=["Date"])
            df["Net Short Volume $"] = df["Net Short Volume $"] / 100_000_000
            df["Short Volume"] = df["Short Volume"] / 1_000_000
            df["Net Short Volume"] = df["Net Short Volume"] / 1_000_000
            df["Short Volume %"] = df["Short Volume %"] * 100
            df["Dark Pools Position $"] = df["Dark Pools Position $"] / (1_000_000_000)
            df["Dark Pools Position"] = df["Dark Pools Position"] / 1_000_000
            df.columns = [
                "Ticker",
                "Short Vol. (1M)",
                "Short Vol. %",
                "Net Short Vol. (1M)",
                "Net Short Vol. ($100M)",
                "DP Position (1M)",
                "DP Position ($1B)",
            ]
            future_column_name = df["Ticker"]
            df = df.transpose()
            df.columns = future_column_name
            df.drop("Ticker")
            columns = []
            initial_str = "Page 0: Overview"
            i = 1
            for column in df.columns.values:
                initial_str = initial_str + "\nPage " + str(i) + ": " + column
                i += 1
            columns.append(
                discord.Embed(
                    title="Stocks: [Stockgrid] Dark Pool Short Position",
                    description=initial_str,
                    colour=cfg.COLOR,
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
            )
            for column in df.columns.values:
                columns.append(
                    discord.Embed(
                        title="High Short Interest",
                        description="```The following data corresponds to the date: "
                        + dp_date
                        + "\n\n"
                        + df[column].fillna("").to_string()
                        + "```",
                        colour=cfg.COLOR,
                    ).set_author(
                        name=cfg.AUTHOR_NAME,
                        icon_url=cfg.AUTHOR_ICON_URL,
                    )
                )

            await pagination(columns, ctx)

    except Exception as e:
        title = "INTERNAL ERROR"
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_description(
            "Try updating the bot, make sure DEBUG is True in the config "
            "and restart it.\nIf the error still occurs open a issue at: "
            "https://github.com/GamestonkTerminal/GamestonkTerminal/issues"
            f"\n{e}"
        )
        await ctx.send(embed=embed)
        if cfg.DEBUG:
            print(e)
