import json
import datetime
import boto3
from boto3.dynamodb.conditions import Attr

def get_date(utterance):
    if utterance == '오늘':
        date = datetime.datetime.today()
    elif utterance == '내일':
        date = datetime.datetime.today() + datetime.timedelta(days=1)
    else:
        days = ['월', '화', '수', '목', '금', '토', '일']
        for i in range(7):
            if utterance == days[i]:
                break
            
        date = datetime.datetime.today()
        # 월요일의 날짜를 구한다.
        date -= datetime.timedelta(days=date.weekday())
        # 월요일의 날짜에 i를 더해 해당 요일의 날짜를 구한다.
        date += datetime.timedelta(days=i)
        
    return date.strftime('%Y%m%d')

def get_menu(date):
    try:
        dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-2")
        table = dynamodb.Table('ssubobbot')
    
        menu = table.scan(
            FilterExpression=Attr('id').begins_with(date)
        )['Items']
    except:
        return {}
    
    return menu

def set_simpleText(utterance):
    if utterance == '처음으로':
        simpleText = {'simpleText' : {'text' : '말해밥'}}
    elif utterance == '요일별':
        simpleText = {'simpleText' : {'text' : '말해밥'}}
    # 메뉴가 없을 경우
    else:
        simpleText = {'simpleText' : {'text' : utterance + '일자 메뉴는 아직 없밥'}}
    return simpleText
    
def set_menu_simpleText(date, menus):
    simpleText = {'simpleText' : {}}
    
    date = date[4:6] + '월 ' + date[6:8] + '일 학식이밥\n\n'
    breakfast = '조식\n* 배식 시간\n기숙사 : 08:00~09:30(주말X)\n'
    lunch = '중식\n* 배식 시간\n식당 : 11:30~14:00\n기숙사 : 11:00~14:00\n'
    dinner = '석식\n* 배식 시간\n식당 : 17:00~18:30\n기숙사 : 17:00~18:30\n'
    
    for menu in menus:
        # 메뉴가 없을 경우
        if not menu['menu']:
            continue
        
        if menu['type'] == '조식':
            breakfast = breakfast + '[' + menu['location'] + ']\n' + menu['menu'] + '\n'
        elif menu['type'] == '중식':
            lunch = lunch + '[' + menu['location'] + ']\n' + menu['menu'] + '\n'
        else:
            dinner = dinner + '[' + menu['location'] + ']\n' + menu['menu'] + '\n'
            
    simpleText['simpleText']['text'] = date + breakfast + '\n' + lunch + '\n' + dinner
    
    return simpleText
    
'''
메뉴를 다 못담아서 보류
def set_menu_carousel(menus):
    carousel = {'carousel' : {}}
    carousel['type'] = 'basicCard'
    
    items = []
    fields = ['title', 'description', 'thumbnail']
    # 배식 시간 안내
    items.append({fields[0] : '배식 시간', fields[1] : '식당 배식시간\n중식 : 11:30~14:00\n석식 : 17:00~18:30\n기숙사 배식시간\n조식 : 08:00~09:30\n중식 : 11:00~14:00\n석식 : 17:00~18:30', fields[2] : 'http://k.kakaocdn.net/dn/83BvP/bl20duRC1Q1/lj3JUcmrzC53YIjNDkqbWK/i_6piz1p.jpg'})
    
    for menu in menus:
        # 메뉴가 없을 경우
        if not menu['menu']:
            continue
            
        items.append({fields[0] : menu['type'] + ' - ' + menu['location'], fields[1] : menu['menu'], fields[2] : 'http://k.kakaocdn.net/dn/83BvP/bl20duRC1Q1/lj3JUcmrzC53YIjNDkqbWK/i_6piz1p.jpg'})
    
    carousel['items'] = items
    carousel = {'carousel' : carousel}
    
    return carousel
'''

def set_quickReplies(utterance):
    quickReplies = []
    
    fields = ['label', 'action', 'messageText']
    
    if utterance == '처음으로':
        for_home = ['오늘', '내일', '요일별']
        
        for label in for_home:
            reply = {fields[0] : label, fields[1] : 'message', fields[2] : label}
            quickReplies.append(reply)
    elif utterance == '요일별':
        for_days = ['월', '화', '수', '목', '금', '토', '일', '처음으로']
        
        for day in for_days:
            reply = {fields[0] : day, fields[1] : 'message', fields[2] : day}
            quickReplies.append(reply)
    else:
        reply = {fields[0] : '처음으로', fields[1] : 'message', fields[2] : '처음으로'}
        quickReplies.append(reply)
    
    return quickReplies
    
def lambda_handler(event, context):
    request = json.loads(event['body'])
    utterance = request['userRequest']['utterance']
    
    result = {
        "version": "2.0",
        "template": {
            'outputs' : []
        }
    }
    
    result['template']['quickReplies'] = set_quickReplies(utterance)
    
    if utterance == '처음으로' or utterance == '요일별':
        result['template']['outputs'].append(set_simpleText(utterance))
    else:
        date = get_date(utterance)
        menu = get_menu(date)

        # 메뉴가 없을 경우(가능한 경우 : 일요일에 내일 메뉴를 물어봤을 경우)
        if not menu:
            result['template']['outputs'].append(set_simpleText(date))
        else:
            result['template']['outputs'].append(set_menu_simpleText(date, menu))

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
