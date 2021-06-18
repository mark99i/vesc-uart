class RequestPacket:
    client_ip:str = ""
    proxy_ip:str = None

    method:str = ""
    full_url:str = ""
    api_endpoint:str = ""
    user_agent:str = ""

    body = ""
    json_root:dict = dict()

    requested_indent = 4
    headers = []