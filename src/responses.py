import asyncio, discord, json, os, re

DEFAULT_PREFIX="!"

async def get_status(ip:str) -> bool:
    ip, port = ip.split(":")
    await asyncio.create_subprocess_exec(f"auto_status.exe", f"{ip}", f"{port}")
    with open("data/pass.json", "r") as fp:
        contents = json.load(fp)
        return contents
    
def set_ip(server:int, ip:str) -> bool:
    try:
        if os.path.isfile('data/server.json') is False:
            raise Exception("File not found")
        with open('data/server.json', 'r') as fp:
            contents = json.load(fp)
            contents["guilds"][str(server)]["ip"] = ip
        with open('data/server.json', 'w') as fp:
            json.dump(contents, fp, indent=4, separators=(',',': '))
        return True
    except:
        return False

def to_embed(title:str, header:str, text:str) -> discord.Embed:
    embed = discord.Embed(title=title,color=0xffa6a6)
    embed.add_field(name=header, value=text)
    return embed

def get_args(message:str) -> list:
    args = message.split(" ")
    args.pop(0)
    while '' in args:
        args.remove('')
    return args

async def auto_status(message:discord.Message, server:int, ip:str):
    with open("data/server.json", "r") as fp:
        contents = json.load(fp)
        contents["guilds"][str(server)]["auto_status_active"] = True
    with open("data/server.json", "w") as fp:
        json.dump(contents, fp, indent=4, separators=(',',': '))
    while True:
        with open("data/server.json") as fp:
            contents = json.load(fp)
            do_continue = bool(contents["guilds"][str(server)]["auto_status_active"])
        if not do_continue:
            break
        status1 = await get_status(ip)
        await asyncio.sleep(1)
        status2 = await get_status(ip)
        if status1 != status2:
            await message.channel.send(embed=to_embed(f"Auto Status for: {ip}", "Status has now changed to:", str(status2)))

def get_ip(guild:int) -> str:
    with open("data/server.json", 'r') as fp:
        contents = json.load(fp)
        ip = contents["guilds"][str(guild)]["ip"]
    return ip

async def handle_responses(message:discord.Message, user_message:str, guild_id:int, is_command:bool, pref:str=DEFAULT_PREFIX):
    p_message = user_message.lower()

    if is_command:
        if p_message.startswith("help"):
            return to_embed(f"Command: {pref}help", "List of commands:", """!help: desplays this message
            !setip: sets the ip to be checked
            !getstatus: gets the status of the set ip
            !autostatus: automatically detects detects and sends changes to the server status""")
        
        if p_message.startswith("setip"):
            ip = get_args(p_message)[0] 
            is_succeed = set_ip(guild_id, ip)
            if is_succeed:
                if (re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$").match(ip) or 
                    re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$").match(ip)):
                    
                    return to_embed(f"Command: {pref}setip", "Succeed state:", str(True))
                else:
                    return to_embed(f"Command: {pref}setip", "Warning:", "IP has been set but may not match these formats: ip or hostname")
            else:
                return to_embed(f"Command: {pref}setip", "Succeed state:", str(False))
        
        if p_message.startswith("getstatus"):
            ip = get_ip(guild_id)
            if await get_status(ip):
                return to_embed(f"Command: {pref}getstatus", "Server state:", "active")
            else:
                return to_embed(f"Command: {pref}getstatus", "Server state:", "inactive")
        
        if p_message.startswith("autostatus"):
            try:
                ip = get_ip(guild_id)
            except:
                return to_embed(f"Command: {pref}autostatus", "Error:", "ip has not been set")
            
            try:
                arg = get_args(p_message)[0]
                if arg == 'true':
                    is_true = True
                elif arg == 'false':
                    is_true = False
                else:
                    raise ValueError
            except:
                return to_embed(f"Command: {pref}autostatus", "Incorrect argument:", "arguments: true/ false")
            
            if is_true:
                loop = asyncio.get_event_loop()
                loop.create_task(auto_status(message, guild_id, ip))
                loop.run_until_complete()
                return to_embed(f"Command: {pref}autostatus", "Is active:", "true")
            else:
                with open("data/server.json", "r") as fp:
                    contents = json.load(fp)
                    contents["guilds"][str(guild_id)]["auto_status_active"] = False
                with open("data/server.json", "w") as fp:
                    json.dump(contents, fp, indent=4, separators=(',',': '))
                return to_embed(f"Command: {pref}autostatus", "Is active:", "false")