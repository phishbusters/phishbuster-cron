import asyncio
from twscrape import API, gather
from twscrape.logger import set_log_level
from twscrape.models import parse_users

async def main():
    api = API()  # or API("path-to.db") - default is `accounts.db`
    # await api.pool.delete_accounts('user1')
    # ADD ACCOUNTS (for CLI usage see BELOW)
    cookies="guest_id_marketing=v1%3A169394984442405202; guest_id_ads=v1%3A169394984442405202; personalization_id=\"v1_Uxk7ypSKxTWkiY9yfFl6/g==\"; guest_id=v1%3A169394984442405202; gt=1699174919584571872; ct0=e58659e2a7cf5b136d3166ef5d42989aca81d5afdaf574714bbb3a900e05f4765591d8bc1341451d4e14a64415550fcf06b681f7c0febf4f15bc41707fe51f9d968016684414e11d8e0cc91e007c5a03; _twitter_sess=BAh7BiIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7AA%253D%253D--1164b91ac812d853b877e93ddb612b7471bebc74; kdt=bLKcrTJvXPOC9kASbZy1cZUm7xzoU4bRzNOj800Z; twid=u%3D1699175315786915840; auth_token=522f2e046a0ec71849fe04cd90347b3031200921; lang=en"
    await api.pool.add_account("MiraFercho76833", "Ferchu$$91", "fernandomirabile5@gmail.com", "Ferchu$$91", cookies=cookies)
    await api.pool.login_all()
    # await api.pool.login("MiraFercho76833")

    # print(await gather(api.search("uala argentina")))
    # change log level, default info

    await gather(api.search_raw("Uala Argentina", kv={"product": "People"}, limit=20))
    print(await api.user_by_login("FerMirabile"))

    # async for rep in api.search_raw("uala argentina", limit=20):
    #     for x in parse_users(rep.json(), 1):
    #         print(x)

    set_log_level("DEBUG")

if __name__ == "__main__":
    asyncio.run(main())