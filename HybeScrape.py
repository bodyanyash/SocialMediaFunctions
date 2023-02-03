from urllib.request import Request, urlopen
import requests
import torpy
from fake_useragent import UserAgent
import random
from bs4 import BeautifulSoup
from IPython.core.display import clear_output
from torpy.http.requests import TorRequests

# Here I provide some proxies for not getting caught while scraping


# Main function
def main(ua):
    # Retrieve latest proxies
    proxies = proxy_list(ua)

    # Choose a random proxy
    proxy_index = random_proxy()
    proxy = proxies[proxy_index]

    for n in range(1, 20):
        req = Request('http://icanhazip.com')
        req.set_proxy(proxy['ip'] + ':' + proxy['port'], 'http')

        # Every 10 requests, generate a new proxy
        # if n % 10 == 0:
        proxy_index = random_proxy(proxies)
        proxy = proxies[proxy_index]

        # Make the call
        try:
            my_ip = urlopen(req).read().decode('utf8')
            print('#' + str(n) + ': ' + my_ip)
            clear_output(wait=True)
        except:  # If error, delete this proxy and find another one
            del proxies[proxy_index]
            print('Proxy ' + proxy['ip'] + ':' + proxy['port'] + ' deleted.')
            proxy_index = random_proxy(proxies)
            proxy = proxies[proxy_index]


# Get the list of proxies
def proxy_list(ua):
    proxies = []
    proxies_req = Request('https://www.sslproxies.org/')
    proxies_req.add_header('User-Agent', ua.random)
    proxies_doc = urlopen(proxies_req).read().decode('utf8')

    soup = BeautifulSoup(proxies_doc, 'html.parser')
    proxies_table = soup.find(id='proxylisttable')

    # Save proxies in the array
    for row in proxies_table.tbody.find_all('tr'):
        proxies.append({
            'ip': row.find_all('td')[0].string,
            'port': row.find_all('td')[1].string
        })
    return proxies


# Retrieve a random index proxy (we need the index to delete it if not working)
def random_proxy(proxies=[{'ip': '127.0.0.1', 'port': '8080'}]):
    return random.randint(0, len(proxies) - 1)


user_agent_list = (
    # Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    # Firefox
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
)


# ua = UserAgent()  # From here we generate a random user agent
# main(ua)
def TenDigs():
    digits = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    digitz = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    str = ''
    for i in range(10):
        if i == 0:
            str = str + random.choice(digitz)
        else:
            str = str + random.choice(digits)
    return str


client = torpy.TorClient()
email = "ertert@anonmails.de"
nickname = "ruyrsr"
cid = TenDigs() + '.' + TenDigs()


session = requests.session()
# Tor uses the 9050 port as the default socks port
session.proxies = {'http':  'socks5://127.0.0.1:9150',
                    'https': 'socks5://127.0.0.1:9150'}
data = {"email": email,
        "password": 'qweqwe',
                "nickname": nickname,
                "friendReferralCode": "ertert",
                "giftGivingIdentifier": "",
                "legalConsent": True,
                "promoConsent": False,
                "cid": cid,
                "registrationMethod": "EMAIL",
                "debug": True}
#print(session.post("https://api.hybe.com/api/public/user", json=data).text)

print(session.post("https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=AIzaSyCAv3D6iwDrDRbrCTyUyehrqlq1QGtUeTg", json=data).text)

'''
with TorRequests() as tor_requests:
    with tor_requests.get_session() as sess:
        data = {"email": email,
                "nickname": nickname,
                "friendReferralCode": "ertert",
                "giftGivingIdentifier": "",
                "legalConsent": True,
                "promoConsent": False,
                "cid": cid,
                "registrationMethod": "EMAIL"}

        response = sess.post("https://api.hybe.com/api/public/user", data=data)  # fire request
        print(response.text)
        
        
proxies = []  # Will contain proxies [ip, port]
proxies = proxy_list()
browsers = ['chrome', 'internetexplorer', 'firefox', 'safari', 'opera']
user_agent = random.choice(ua.data_browsers[random.choice(browsers)])
headers = {'User-Agent': user_agent, "Accept-Language": "en-US, en;q=0.5"}
proxy = random.choice(proxies)
#response = requests.get("http://icanhazip.com", headers=headers, proxies=proxy)
print(proxy)


user_agent = random.choice(user_agent_list)


'''
