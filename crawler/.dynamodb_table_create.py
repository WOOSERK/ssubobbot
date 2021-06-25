import re
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ssubobbot')

response = table.scan(
    FilterExpression=Attr('id').begins_with('202105')
)['Items']

for menu in response:
    if menu['location'] == '기숙사':
        temp = menu['menu']
        break

temp = re.sub(r'[\n]', ', ', temp)
print(temp)
