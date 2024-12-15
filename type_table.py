from __future__ import print_function
import mysql.connector
from mysql.connector import errorcode

DB_NAME = 'typeDB'

TABLES={'sentences'}
TABLES['sentences']=(
    "CREATE TABLE `sentences` ()"
    "`id` INT AUTO_INCREMENT PRIMARY KEY, " #고유 ID, 자동 증가, primary key
    "`sentence` TEXT NOT NULL" #문장 (최대 글자수 제한 없음)
)

connection = mysql.connector.connect(user="cloud4")
cursor = connection.cursor()

add_sentence = (
    "INSERT INTO sentences (sentence) VALUES"
    "('체다치즈를 최고 많이 먹은 최다연이 체다치즈 먹기 대회 최다 우승자이다.'),"
    "('정희수가 희희낙락하게 희끄무리한 흰머리를 뽑으며'),"
    "('이수지가 저수지에 갔는데 이 수지가 저수지에 간 걸까 저 수지가 저수지에 간걸까'),"
    "('그 수지가 저수지에 간 걸까 하며 이수지는 고민했는데 고민 끝에 이수의 마이웨이를 부르며 불쾌지수가 올라가며'),"
    "('저수지를 떠나 경기도 수지구의 한 학원으로 달려가더니 지수함수를 배워서 잘 사용하여 주식 수지를 맞아'),"
    "('나 이수지, 바로 고단수지! 수지맞았다!하며 행복해했다.'),"
    "('내가 그린 기린 그림은 잘 그린 기린 그림이고 네가 그린 기린 그림은 못 그린 기린 그림이다.'),"
    "('내가 그린 기린 그림은 목이 긴 기린 그린 그림이고, 네가 그린 기린 그림은 목이 안 긴 기린 그린 그림이다'),"
    "('내가 그린 구름그림은 새털구름 그린 구름그림이고, 네가 그린 구름그림은 깃털구름 그린 구름그림이다.'),"
    "('저기 계신 저 분이 박 법학박사이시고 여기 계신 이 분이 백 법학박사이시다.'),"
    "('김혜진, 류미성, 문채일 함께 만든 게임입니다. '),"
    "('클라우드 시스템 짱!');"
    # "(sentence) VALUES"
)



def create_db(cursor):
    try:
        # create database
        cursor.execute(
            f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET 'utf8'"
        )
        # create table
        for table_name in TABLES:
            table_description = TABLES[table_name]
            try:
                print(f"Creating table {table_name}", end='') # 확인용

                # insert data
                cursor.execute(table_description)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists.")
                else:
                    print(err.msg)

    except mysql.connector.Error as e:
        print(f"Failed creating database: {e}")


try:
    create_db(cursor)
    # cursor.execute(f"USE {DB_NAME}")
except mysql.connector.Error as e:
    print(f"Database {DB_NAME} does not exist.")
finally:
        cursor.close()
        connection.close()