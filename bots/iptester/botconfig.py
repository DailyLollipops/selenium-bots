config = {
    # Bot id name
    "id": "iptester",

    # Bot name
    "name": "IP tester",

    # Bot description
    "name": "IP tester",

    # Timeout for DriverWait
    "timeout": 30,
    "pageTimeout": 60,

    # Other configs (e.g. selectors, xpaths)
    "mainUrl": "https://whatismyipaddress.com/",
    "ipV4Xpath": "//p[contains(text(), 'IPv4')]/span[2]",
    "ipV6Xpath": "//p[contains(text(), 'IPv6')]/span[2]",
}
