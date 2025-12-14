# -------------------------------
# models.py
# -------------------------------
# ไฟล์นี้ใช้กำหนดโครงสร้างฐานข้อมูล (Database Model)
# โดยใช้ SQLAlchemy ซึ่งเป็น ORM (Object Relational Mapper)
# ORM จะช่วยให้เราเขียนโค้ด Python แทนการเขียน SQL ตรง ๆ
# -------------------------------

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

# สร้าง instance ของ SQLAlchemy
# ตัวแปร db นี้จะถูกนำไปใช้ใน app.py เพื่อเชื่อมกับ Flask app
db = SQLAlchemy()

# -------------------------------
# ฟังก์ชันคืนค่าเวลาปัจจุบัน (UTC)
# -------------------------------
# เหตุผลที่ใช้ฟังก์ชัน:
# - SQLAlchemy ต้องการ callable (ฟังก์ชัน)
# - เพื่อให้เวลาถูกสร้าง "ตอนเพิ่มข้อมูลจริง"
# - ไม่ใช่ตอนโหลดไฟล์
def now_utc():
    return datetime.now(timezone.utc)

# -------------------------------
# Product Model
# -------------------------------
# คลาสนี้แทน "ตารางสินค้า" ในฐานข้อมูล
# แต่ละ attribute = 1 column ในตาราง
class Product(db.Model):

    # ชื่อตารางใน SQLite
    __tablename__ = 'products'

    # ---------------------------
    # Primary Key
    # ---------------------------
    # id เป็นเลขอัตโนมัติ (auto increment)
    # ใช้เป็นตัวระบุแถวในฐานข้อมูล
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ---------------------------
    # รหัสสินค้า
    # ---------------------------
    # unique=True หมายถึงห้ามซ้ำ
    # nullable=False หมายถึงห้ามเป็นค่าว่าง
    product_code = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    # ---------------------------
    # ชื่อสินค้า
    # ---------------------------
    name = db.Column(
        db.String(200),
        nullable=False
    )

    # ---------------------------
    # ราคาสินค้า
    # ---------------------------
    # ใช้ Float เพื่อรองรับราคาที่มีทศนิยม
    price = db.Column(
        db.Float,
        nullable=False
    )

    # ---------------------------
    # ชื่อไฟล์รูปสินค้า
    # ---------------------------
    # เก็บเฉพาะชื่อไฟล์ เช่น "P001.jpg"
    # ตัวไฟล์จริงจะอยู่ในโฟลเดอร์ media/products/
    image_filename = db.Column(
        db.String(300),
        nullable=True
    )

    # ---------------------------
    # เวลาที่เพิ่มข้อมูล
    # ---------------------------
    # ใช้เวลาแบบ UTC (timezone-aware)
    # เรียกฟังก์ชัน now_utc ทุกครั้งที่ INSERT
    created_at = db.Column(
        db.DateTime,
        default=now_utc
    )

    # ---------------------------
    # แปลง object → dictionary
    # ---------------------------
    # ใช้เวลาส่งข้อมูลออกทาง API (jsonify)
    def to_dict(self):
        return {
            "id": self.id,
            "product_code": self.product_code,
            "name": self.name,
            "price": self.price,
            "image_filename": self.image_filename,
            "created_at": self.created_at.isoformat()
        }
