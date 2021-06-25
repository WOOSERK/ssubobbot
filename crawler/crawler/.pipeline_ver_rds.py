# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import sys
import logging
import pymysql

from itemadapter import ItemAdapter

class CrawlerPipeline:
    # 최초 1회 실행. 연결 확립
    def __init__(self):
        self.conn, self.cursor = connect_RDS()
        # 한글 설정
        self.cursor.execute('set names utf8')

    def spider_opened(self, spider):
        spider.logger.info("RDS 연결 성공")

    def process_item(self, item, spider):
        query = '''
            insert into meal(date, time, location, menu)
            values('{0}', '{1}', '{2}', '{3}')
            on duplicate key update date = '{0}', time = '{1}', location = '{2}', menu = '{3}'
            '''.format(item['date'], item['time'], item['location'], item['menu'])

        self.cursor.execute(query)
        self.conn.commit()
        return item

    def spider_closed(self, spider):
        self.cursor.close()
        self.conn.close()
        spider.logger.info("RDS INSERT 완료")

def connect_RDS():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)

        host = config['RDS']['HOST']
        port = config['RDS']['PORT']
        username = config['RDS']['USERNAME']
        password = config['RDS']['PASSWORD']
        database = config['RDS']['DATABASE']

        conn = pymysql.connect(
                host = host,
                user = username,
                port = port, 
                passwd = password,
                db = database,
                charset = 'utf8')

        cursor = conn.cursor()

    except:
        logging.error("RDS 연결 실패")
        sys.exit(1)

    finally:
        f.close()

    return conn, cursor
