# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import sys
import logging
import boto3

from itemadapter import ItemAdapter

class CrawlerPipeline:
    # 최초 1회 실행
    def __init__(self):
        try:
            self.dynamodb = boto3.resource('dynamodb')
            self.table = self.dynamodb.Table('ssubobbot')
        except:
            logging.error("dynamoDB 연결 실패")
            sys.exit(1)

    def spider_opened(self, spider):
        spider.logger.info("dynamoDB 연결 성공")

    def process_item(self, item, spider):
        if item['time'] == '조식':
            timecode = '00'
        elif item['time'] == '중식':
            timecode = '01'
        else:
            timecode = '02'

        location = ['기숙사', '학생식당 1코너', '학생식당 3코너', '숭실도담', 'FACULTY LOUNGE']
        for i in range(5):
            if item['location'] == location[i]:
                locationcode = '0' + str(i)
                break

        self.table.put_item(
            Item = {
                'id' : item['date'] + timecode + locationcode,
                'type' : item['time'],
                'location' : item['location'],
                'menu' : item['menu']
            }
        )

        return item

    def spider_closed(self, spider):
        spider.logger.info("데이터베이스 입력 완료")
