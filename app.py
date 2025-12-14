# ----------------------------------------
# app.py
# ----------------------------------------
# จุดประสงค์:
# - สร้าง Flask app
# - เชื่อมกับ SQLite
# - จัดการ route สำหรับหน้าเว็บทั้งหมด
# - จัดการ API สำหรับเพิ่มสินค้า, ค้นหา, และดึงสินค้าทั้งหมด
# ----------------------------------------

import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from models import db, Product

# ----------------------------------------
# สร้าง Flask application
# ----------------------------------------
app = Flask(__name__)

# ----------------------------------------
# ตั้งค่าฐานข้อมูล
# ----------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# products.db จะถูกสร้างอัตโนมัติในโฟลเดอร์นี้
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'products.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ----------------------------------------
# ตั้งค่าโฟลเดอร์เก็บรูปสินค้า
# ----------------------------------------
MEDIA_FOLDER = os.path.join(BASE_DIR, "media", "products")
app.config["MEDIA_FOLDER"] = MEDIA_FOLDER

# ถ้ายังไม่มี ให้สร้างโฟลเดอร์
os.makedirs(MEDIA_FOLDER, exist_ok=True)

# ----------------------------------------
# เชื่อม SQLAlchemy กับ Flask app
# ----------------------------------------
db.init_app(app)

# ----------------------------------------
# สร้างตารางฐานข้อมูลตาม model
# ----------------------------------------
with app.app_context():
    db.create_all()

# ----------------------------------------
# ROUTE: หน้าเพิ่มสินค้า (index)
# ----------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

# ----------------------------------------
# ROUTE: หน้า search (index2)
# ----------------------------------------
@app.route("/search")
def search_page():
    return render_template("index2.html")

# ----------------------------------------
# ROUTE: หน้าแสดงสินค้าทั้งหมด (index3)
# ----------------------------------------
@app.route("/view")
def view_page():
    return render_template("index3.html")

# ----------------------------------------
# ROUTE: หน้าแสดงสินค้าทั้งหมด (index4)
# ----------------------------------------
@app.route("/del")
def delete_page():
    return render_template("index4.html")

# ----------------------------------------
# ROUTE: serve รูปสินค้า
# ----------------------------------------
@app.route("/media/products/<filename>")
def get_product_image(filename):
    # ส่งไฟล์รูปจากโฟลเดอร์ media/products
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)

# ----------------------------------------
# API: เพิ่มสินค้า
# ----------------------------------------
@app.route("/api/products", methods=["POST"])
def add_product():
    product_code = request.form.get("product_code")
    name = request.form.get("name")
    price = request.form.get("price")
    image = request.files.get("image")

    # ตรวจข้อมูลเบื้องต้น
    if not product_code or not name or not price:
        return jsonify({"error": "กรุณากรอกข้อมูลให้ครบ"}), 400

    # ตรวจว่ารหัสซ้ำไหม
    if Product.query.filter_by(product_code=product_code).first():
        return jsonify({"error": "รหัสสินค้าซ้ำ"}), 400

    image_filename = None
    if image and image.filename != "":
        filename = secure_filename(image.filename)
        ext = os.path.splitext(filename)[1]
        image_filename = f"{product_code}{ext}"
        image_path = os.path.join(app.config["MEDIA_FOLDER"], image_filename)
        image.save(image_path)

    # สร้าง product ใหม่
    product = Product(
        product_code=product_code,
        name=name,
        price=float(price),
        image_filename=image_filename
    )

    db.session.add(product)
    db.session.commit()

    return jsonify({"message": "สินค้าเพิ่มแล้ว", "product": product.to_dict()}), 201

# ----------------------------------------
# API: ค้นหาสินค้าจากรหัส
# ----------------------------------------
@app.route("/api/products/<product_code>", methods=["GET"])
def get_product(product_code):
    product = Product.query.filter_by(product_code=product_code).first()
    if not product:
        return jsonify({"error": "ไม่พบสินค้า"}), 404

    image_url = None
    if product.image_filename:
        image_url = f"/media/products/{product.image_filename}"

    return jsonify({
        "product_code": product.product_code,
        "name": product.name,
        "price": product.price,
        "image_url": image_url,
        "created_at": product.created_at.isoformat()
    }), 200

# ----------------------------------------
# API: ดึงสินค้าทั้งหมด
# ----------------------------------------
@app.route("/api/products", methods=["GET"])
def get_all_products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    result = []
    for p in products:
        image_url = None
        if p.image_filename:
            image_url = f"/media/products/{p.image_filename}"
        result.append({
            "product_code": p.product_code,
            "name": p.name,
            "price": p.price,
            "image_url": image_url,
            "created_at": p.created_at.isoformat()
        })
    return jsonify(result), 200

@app.route("/api/products/<product_code>", methods=["DELETE"])
def delete_product(product_code):
    """
    API สำหรับลบสินค้าตามรหัสสินค้า
    - product_code ใช้เป็น identifier สำหรับลบ
    """

    # 1) หา product จากฐานข้อมูล
    product = Product.query.filter_by(product_code=product_code).first()
    if not product:
        # ถ้าไม่พบ → ส่ง error
        return jsonify({"error": "ไม่พบสินค้า"}), 404

    # 2) ถ้ามีรูปสินค้า ให้ลบไฟล์
    if product.image_filename:
        image_path = os.path.join(app.config["MEDIA_FOLDER"], product.image_filename)
        # เช็คก่อนว่ามีไฟล์จริงหรือไม่
        if os.path.exists(image_path):
            os.remove(image_path)

    # 3) ลบ record จากฐานข้อมูล
    db.session.delete(product)
    db.session.commit()

    # 4) ส่งผลลัพธ์กลับเป็น JSON
    return jsonify({"message": f"ลบสินค้า {product_code} เรียบร้อยแล้ว"}), 200


# ----------------------------------------
# รันแอป (เมื่อเรียกไฟล์นี้โดยตรง)
# ----------------------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
