from typing import List
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import os
from datetime import date
import pymysql

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mechanic.db'

#========== Database Connection ==========

class Base(DeclarativeBase):
    pass

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

with app.app_context():
    db.create_all()
    # db.session.commit()
    # new_customer = Customer(name="James",email="realemail@email.com", phone="205457894")
    # db.session.add(new_customer)
    # db.session.commit()
    customer = db.session.get(Customer, 1)
    print(customer.name)








if __name__ == '__main__':
    app.run()
