from typing import List
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
from sqlalchemy import Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import date
import pymysql
from flask_marshmallow import Marshmallow
import sys
print(sys.path)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mechanic.db'

#========== Database Connection ==========

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
ma = Marshmallow()

db = SQLAlchemy(model_class=Base)
db.init_app(app) 

# ========== Models ==========

service_mechanics = db.Table(
    "service_mechanics",
    Base.metadata,
    Column("ticket_id", db.ForeignKey("service_tickets.id")),
    Column("mechanic_id", db.ForeignKey("mechanics.id"))
)

class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(200), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(20))

    # One-to-Many
    service_tickets: Mapped[List['Service_Ticket']] = relationship(back_populates='customer')

class Service_Ticket(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(db.String(100), nullable=False)
    service_date: Mapped[date] = mapped_column(nullable=False)
    service_desc: Mapped[str] = mapped_column(db.String(100), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'))

    # Many-to-One
    customer: Mapped['Customer'] = relationship(back_populates='service_tickets')
    # Many-to-Many
    mechanics: Mapped[List['Mechanic']] = relationship(secondary=service_mechanics, back_populates='service_tickets')

class Mechanic(Base):
    __tablename__ = 'mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(100), nullable=False)
    phone: Mapped[str] = mapped_column(db.String(50), nullable=False)
    salary: Mapped[float] = mapped_column( nullable=False)

    service_tickets: Mapped[List['Service_Ticket']] = relationship(secondary=service_mechanics, back_populates='mechanics')

#============ Schema ============

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
       

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Service_Ticket
        

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
       

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)

#========== Routes ==========

@app.route('/customers', methods=['POST'])
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
        
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
    db.session.add(new_customer)
    db.session.commit()

    return customer_schema.jsonify(new_customer), 201

@app.route('/customers', methods=["GET"])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    return customer_schema.jsonify(customer), 200


@app.route('/customers/<int:customer_id>', methods=["PUT"])
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer == None:
        return jsonify({'message': 'invalid_id'}), 400
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in customer_data.items():
        if value:
            setattr(customer, field, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200

@app.route('/customers/<int:customer_id>', methods=["DELETE"])
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer == None:
        return jsonify({'message': 'invalid_id'}), 400

    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': f'successfully deleted customer {customer_id}!'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # db.session.commit()
        # new_customer = Customer(name="James",email="realemail@email.com", phone="205457894")
        # db.session.add(new_customer)
        # db.session.commit()
        # customer = db.session.get(Customer, 1)
        # print(customer.name)


    app.run(debug=True)
