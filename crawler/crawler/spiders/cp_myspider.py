from types import DynamicClassAttribute
from crawler.items import Dormitory, Student
import re
import scrapy
import datetime

class CrawlerSpider(scrapy.Spider):
    name = 'crawler'
    allowed_domains = ['ssudorm.ssu.ac.kr', 'soongguri.com/']
    now = datetime.datetime.today()
    # 학생 식당을 위한 변수
    j = 0
    # 주말이면 다음 주 식단이 보이기 때문에 연산해준다.
    # 일요일
    if now.weekday() == 6:
        now -= datetime.timedelta(days=2)
        j = -1
    # 토요일
    elif now.weekday() == 5:
        now -= datetime.timedelta(days=1)

    start_urls = ['https://ssudorm.ssu.ac.kr:444/SShostel/mall_main.php?viewform=B0001_foodboard_list&gyear=' + str(now.year) + '&gmonth=' + str(now.month) + '&gday=' + str(now.day), 'https://soongguri.com/main.php?mkey=2&w=3&l=2&j=' + str(j)]

    def parse(self, response):
        # 기숙사 식당
        if response.url == self.start_urls[0]:
            for item in self.parse_dormitory(response):
                yield item
        # 학생 식당, 도담 식당, FACULTY LOUNGE
        else:
            for item in self.parse_student(response):
                yield item

    def extractMenu(self, list):
        ret = []

        for attr in list:
            st = ''
            # div만 파싱한다.
            menus = attr.css('div').xpath('string()').extract()
            if len(menus) >= 2:
                index = 1

                for i in range(0, len(menus)):
                    menus[i] = re.sub(r'[\xa0]', '', menus[i])

                while index < len(menus):
                    if menus[index] != '' and ((menus[index][0] >= 'A' and menus[index][0] <= 'Z') or (menus[index][0] >= 'a' and menus[index][0] <= 'z')) :
                        index -= 1
                        while menus[index] == '':
                            index -= 1

                        break

                    index += 1

                if index < len(menus):
                    st = menus[index]

                '''
                index = menus.index('') + 1
                # 여러 줄 띄워져 있을 경우를 대비
                while st == '':
                    print('zz' + st)
                    st = re.sub(r'[\xa0]', '', menus[index])
                    index+=1
                    if index >= len(menus):
                        break
                '''

            # 문자열이 없으면 메뉴가 없는 것
            ret.append(st)

        return ret

    def parse_dormitory(self, response):
        date = datetime.datetime.today()

        # 월요일부터 기록
        date -= datetime.timedelta(days=date.weekday())

        menus = response.css('tbody tr td').xpath('string()').extract()
        location = '기숙사'
        time = ['조식', '중식', '석식']

        i = 0
        for menu in menus:
            item = Dormitory()

            # 홈페이지의 [중.석식]란은 제외한다.
            if i % 4 == 3:
                i += 1
                continue

            menu = re.sub(r'[\r\t ]', '', menu)
            # 맨 앞의 개행은 지운다.
            menu = re.sub(r'^[\n]', '', menu)
            menu = re.sub(r'[\n]', ', ', menu)

            #휴일 조식은 운영X
            if '않습니다' in menu:
                menu = ''

            item['date'] = (date + datetime.timedelta(days=i//4)).strftime('%Y%m%d')
            item['time'] = time[i%4]
            item['location'] = location
            item['menu'] = menu

            i += 1

            yield item

    def parse_student(self, response):
        date = datetime.datetime.now()

        # 월요일부터 기록
        date -= datetime.timedelta(days=date.weekday())

        menus = response.css('[class^=menu-list]')

        # response.css('.rest-ico ~ div').extract()

        meals = []

        # 점심 1코너가 없어져서 3으로 변경
        lim = 3
        # lim = 4
        # 점심 3코너가 입력됐을 경우
        '''
        if menus[7].css('td').xpath('string()').extract() == '점심 3코너':
            lim = 5
        '''

        for i in range(0, lim):
            meals.append(self.extractMenu(menus[7*i + 1 : 7*i + 6]))

        '''
        stc1 = menus[1:6]
        stc1 = self.extractMenu(stc1)
        # 없을 때가 있음
        stc2 = menus[8:13]
        stc2 = self.extractMenu(stc2)
        dodLun = menus[15:20]
        dodLun = self.extractMenu(dodLun)
        dodDin = menus[22:27]
        dodDin = self.extractMenu(dodDin)
        flg1 = menus[29:34]
        flg1 = self.extractMenu(flg1)
        '''

        '''
        # 조식이 없음
        # 학생식당이 없어져서 4에서 3으로 변경
        location = ['숭실도담', '숭실도담', 'FACULTY LOUNGE']
        time = ['중식', '석식', '중식']
        '''

        if lim == 4:
            location = ['학생식당 1코너', '숭실도담', '숭실도담', 'FACULTY LOUNGE']
            time = ['중식', '중식', '석식', '중식']
        else:
            location = ['학생식당 1코너', '학생식당 3코너', '숭실도담', '숭실도담', 'FACULTY LOUNGE']
            time = ['중식', '중식', '중식', '석식', '중식']

        data = {}
        # 월화수목금 5일
        for i in range(0, 5):
            #menu = [stc1[i], stc2[i], dodLun[i], dodDin[i], flg1[i]]
            menu = []
            for j in range(0, lim):
                menu.append(meals[j][i])

            day = (date + datetime.timedelta(days=i)).strftime('%Y%m%d')

            for j in range(0, lim):
                item = Student()

                item['date'] = day
                item['time'] = time[j]
                item['location'] = location[j]
                item['menu'] = menu[j]

                yield item
