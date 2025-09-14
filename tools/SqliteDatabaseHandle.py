import sqlite3
import os

db_path = os.path.join(os.getcwd(), "WembleyProjectDatabase.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()

#Thêm các cột mới vào bảng Product, với cột thứ 3 là minDist
# c.execute("ALTER TABLE Product ADD COLUMN ScoreTR REAL;")

c.execute("ALTER TABLE Account ADD COLUMN key TEXT;")
#c.execute("INSERT INTO Product (ProductName, Dp, Param1, Param2, Minradius, Maxradius, ExposureTime, Width, Height, OffsetX, OffsetY, TriggerDelay, LIGHT1, LIGHT2, LIGHT3, LIGHT4) VALUES ('BLACK RUBBER CAP', 1.1, 80, 60, 35, 70, 1750, 2592, 2048, 0, 0, 1.195, 7, 7, 7, 7)")

#Insert dữ liệu vào Account trên hàng tùy chỉnh
# c.execute("""UPDATE Account SET PLCHost = ?, PLCPort = ?, PLCType = ? WHERE rowid = ?;""",  ('192.168.100.14', '4095', 'Q',1))

# Thêm các cột mới vào bảng Account
# c.execute("ALTER TABLE Account ADD COLUMN PLCHost TEXT")
# c.execute("ALTER TABLE Account ADD COLUMN PLCPort INTEGER;")
# c.execute("ALTER TABLE Account ADD COLUMN PLCType TEXT;")

#Insert data
# c.execute("INSERT INTO Account (UserName, PassWord, FullName, Duty, Role) VALUES ('admin', '123', 'Nguyễn Văn A', 'Quản lý', '1234')")

#Create table 
# c.execute("CREATE TABLE ProductHistory (ProductName TEXT, ProductTotal INTEGER, GoodTotal INTEGER, BadTotal INTEGER, DefectiveTotal INTEGER, ShortageTotal INTEGER, StartTime TEXT, EndTime TEXT)"),

# c.execute("CREATE TABLE ProductDefault (ProductName TEXT, Dp REAL, Param1 REAL, Param2 REAL, Minradius INTEGER, Maxradius INTEGER, ExposureTime REAL, Width INTEGER, Height INTEGER, OffsetX INTEGER, OffsetY INTEGER, TriggerDelay REAL)")

# c.execute("CREATE TABLE ProductDefault (ProductName TEXT, minDist INTEGER ,Dp REAL, Param1 INTEGER, Param2 INTEGER, Minradius INTEGER, Maxradius INTEGER, ExposureTime REAL, Width INTEGER, Height INTEGER, OffsetX INTEGER, OffsetY INTEGER, TriggerDelay REAL, LIGHT1 REAL, LIGHT2 REAL, LIGHT3 REAL, LIGHT4 REAL)")

# c.execute("CREATE TABLE ErrorHistory (ErrorName TEXT, ProductName TEXT, ErrorPosition INTEGER, OccurTime TEXT)")

# c.execute("CREATE TABLE ProductHistory (ProductName TEXT, TrayQuantity INTEGER, ProductQuantity INTEGER, ErrorQualify INTEGER, StartTime TEXT, EndTime TEXT)")

# c.execute("CREATE TABLE WorkingHistory (FullName TEXT, Dudy TEXT, ActionName TEXT, ActionTime TEXT)")

#Drop table Account
#c.execute("DROP TABLE Account")
conn.commit()
conn.close()
