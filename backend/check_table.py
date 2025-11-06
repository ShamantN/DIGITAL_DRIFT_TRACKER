import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='s181916k00bvyu8',
    database='ddt'
)
cursor = conn.cursor()
cursor.execute('DESCRIBE user')
result = cursor.fetchall()

print('User table columns:')
for row in result:
    print(f"{row[0]} {row[1]} NULL:{row[2] == 'YES'}")

cursor.close()
conn.close()