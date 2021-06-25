import json
import sys
import logging
import pymysql

def main():
    conn, cursor = connect_RDS()

    # 한글 설정
    cursor.execute('set names utf8')

    query = '''
            insert into meal(date, time, location, menu)
            values('{0}', '{1}', '{2}', '{3}')
            on duplicate key update date = '{0}', time = '{1}', location = '{2}', menu = '{3}'
            '''.format('20210522', '조식', '기숙사', '주말 조식은 없습니다.')

    cursor.execute(query)
    conn.commit()

def connect_RDS():
    with open('config.json', 'r') as f:
        config = json.load(f)

    host = config['RDS']['HOST']
    port = config['RDS']['PORT']
    username = config['RDS']['USERNAME']
    password = config['RDS']['PASSWORD']
    database = config['RDS']['DATABASE']

    try:
        conn = pymysql.connect(
                host = host,
                user = username,
                port = port, 
                passwd = password,
                db = database,
                charset = 'utf8')

        cursor = conn.cursor()

    except:
        logging.error("RDS 연결에 실패했았습니다.")
        sys.exit(1)

    return conn, cursor

if __name__ == "__main__":
    main()
