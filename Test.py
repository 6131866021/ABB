import urllib.parse

value = str([[2,2,2],[0,0,1,0],[0,0,-2,0],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]])

print(value, type(value))

print(urllib.parse.quote_plus(value))

# '%5B%5B2%2C2%2C2%5D%2C%5B0%2C0%2C1%2C0%5D%2C%5B0%2C0%2C-2%2C0%5D%2C%5B9E%2B9%2C9E%2B9%2C9E%2B9%2C9E%2B9%2C9E%2B9%2C9E%2B9%5D%5D'

# criterias%5B%5D=member&criterias%5B%5D=issue
# params = {'criterias[]': ['member', 'issue']}
# criterias = ['member', 'issue']
# params = {
#     'criterias[]': criterias,
# }
# print urllib.urlencode(params)