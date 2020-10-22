import mitmproxy
from mitmproxy import ctx
import brotli

def response(flow):
    if(flow.request.url.startswith('https://api3-core-c-hl.amemv.com/aweme/v2/feed/?')):
        if(flow.request.headers['accept-encoding'] == 'gzip, deflate, br'):
            ctx.log.alert("解压缩\n\n")
            ctx.log.alert(flow.response.text.decode('gbk'))
            data = brotli.decompress(flow.response.content)
            data = data.decode('utf-8')
            ctx.log.alert(data)