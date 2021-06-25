from types import DynamicClassAttribute
from crawler.items import Dormitory, Student
import re
import scrapy
import datetime

class CrawlerSpider(scrapy.Spider):
    name = 'crawler'
    allowed_domains = ['ssudorm.ssu.ac.kr:444', 'soongguri.com/']
    now = datetime.datetime.now()
    # 주말이면 다음 주 식단이 보이기 때문에 연산해준다.
    if now.weekday() == 6:
        now -= datetime.timedelta(days=2)
    elif now.weekday() == 5:
        now -= datetime.timedelta(days=1)

    start_urls = ['https://ssudorm.ssu.ac.kr:444/SShostel/mall_main.php?viewform=B0001_foodboard_list&gyear=' + str(now.year) + '&gmonth=' + str(now.month) + '&gday=' + str(now.day), 'https://soongguri.com/main.php?mkey=2&w=3&l=2']

    def parse(self, response):
        # 기숙사 식당
        if response.url == self.start_urls[0]:
            yield self.parse_dormitory(response)
        # 학생 식당, 도담 식당, FACULTY LOUNGE
        else:
            yield self.parse_student(response)

    def extractMenu(self, list):
        ret = []

        for attr in list:
            st = ''
            menus = attr.css('div').xpath('string()').extract()
            if len(menus) >= 2:
                index = menus.index('') + 1

                # 여러 줄 띄워져 있을 경우를 대비
                while st == '':
                    st = re.sub(r'[\xa0]', '', menus[index])
                    index+=1

            # 문자열이 없으면 메뉴가 없는 것
            ret.append(st)

        return ret

    def parse_dormitory(self, response):
        item = Dormitory()
        date = datetime.datetime.now()

        # 월요일부터 기록
        date -= datetime.timedelta(days=date.weekday())

        meals = response.css('tbody tr td').xpath('string()').extract()
        location = '기숙사'
        time = ['조식', '중식', '석식']

        data = {}
        i = 0
        for meal in meals:
            # 홈페이지의 [중.석식]란은 제외한다.
            if i % 4 == 3:
                i += 1
                continue

            meal = re.sub(r'[\r\t ]', '', meal)
            # 맨 앞의 개행은 지운다.
            meal = re.sub(r'^[\n]', '', meal)

            temp = [time[i%4], location, meal]
            day = (date + datetime.timedelta(days=i//4)).strftime('%Y%m%d')

            if day in data:
                data[day].append(temp)
            else :
                data[day] = [temp]

            i += 1

        item['data'] = data
        return item

    def parse_student(self, response):
        item = Student()
        date = datetime.datetime.now()

        # 월요일부터 기록
        date -= datetime.timedelta(days=date.weekday())

        menus = response.css('[class^=menu-list]')

        stc1 = menus[1:6]
        stc1 = self.extractMenu(stc1)

        stc2 = menus[8:13]
        stc2 = self.extractMenu(stc2)

        dodLun = menus[15:20]
        dodLun = self.extractMenu(dodLun)

        dodDin = menus[22:27]
        dodDin = self.extractMenu(dodDin)

        flg1 = menus[29:34]
        flg1 = self.extractMenu(flg1)

        location = ['학생식당 1코너', '학생식당 3코너', '숭실도담', 'FACULTY LOUNGE']
        # 조식이 없음
        time = ['중식', '석식']
        data = {}
        for i in range(0, 5):
            meal = []
            day = (date + datetime.timedelta(days=i)).strftime('%Y%m%d')

            meal.append([time[0], location[0], stc1[i]])
            meal.append([time[0], location[1], stc2[i]])
            meal.append([time[0], location[2], dodLun[i]])
            # 도담 식당은 석식이 있다.
            meal.append([time[1], location[2], dodDin[i]])
            meal.append([time[0], location[3], flg1[i]])

            data[day] = meal

        item['data'] = data
        return item

