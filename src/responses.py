import asyncio, discord, json, os, re

DEFAULT_PREFIX="!"

async def get_status(ip:str) -> bool:
    ip, port = ip.split(":")
    cmd=f"auto_status.exe {ip} {port}"
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE)
    return await proc.communicate()
    
def set_ip(server:int, ip:str) -> bool:
    try:
        if os.path.isfile('data/server.json') is False:
            raise Exception("File not found")
        with open('data/server.json', 'r') as fp:
            contents = json.load(fp)
            contents["guilds"] = {str(server): {"ip": ip}}
        with open('data/server.json', 'w') as fp:
            json.dump(contents, fp, indent=4, separators=(',',': '))
        return True
    except Exception as e:
        print(e)
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

async def auto_status(message:discord.Message, server:int, ip:str, future:asyncio.Future):
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
            if status2[0] == b'1':
                await message.channel.send(embed=to_embed(f"Auto Status for: {ip}", "Status has now changed to:", 'offline'))
            elif status2[0] == b'0':
                await message.channel.send(embed=to_embed(f"Auto Status for: {ip}", "Status has now changed to:", 'online'))
            else:
                await message.channel.send(embed=to_embed(f"Auto Status for: {ip}", "Error:", "Fatal error has occured in process."))
    future.set_result("Auto Status is finished")
    return future

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
            ip:str = get_args(p_message)[0] 
            is_succeed = set_ip(guild_id, ip)
            if is_succeed:
                if ((re.match('^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$', ip.split(':')[0]) and re.match('\d{1,5}', ip.split(':')[1])) != None or 
                    re.match("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$", ip) != None):
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
                future = asyncio.Future()
                loop = asyncio.get_event_loop()
                loop.run_until_complete(await auto_status(message, guild_id, ip, future))
                return to_embed(f"Command: {pref}autostatus", "Is active:", "true")
            else:
                with open("data/server.json", "r") as fp:
                    contents = json.load(fp)
                    contents["guilds"][str(guild_id)]["auto_status_active"] = False
                with open("data/server.json", "w") as fp:
                    json.dump(contents, fp, indent=4, separators=(',',': '))
                return to_embed(f"Command: {pref}autostatus", "Is active:", "false")