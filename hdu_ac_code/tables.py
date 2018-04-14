from sqlalchemy import Column, String, create_engine, Integer, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # 生成一个SqlORM 基类
engine = create_engine("mysql+mysqldb://username:passwd@host:port/dbname?charset=utf8", echo=True,encoding='utf-8')


# echo如果为True，那么当他执行整个代码的数据库的时候会显示过程
# 创建一个类继承Base基类
class HduAcCode(Base):
    # 表名为hosts
    __tablename__ = 'hdu_ac_code'
    # 表结构
    # primary_key等于主键
    # unique唯一
    # nullable非空
    id = Column(Integer, primary_key=True, autoincrement=True)
    problem_id = Column(Integer, unique=True, nullable=False)
    status = Column(Integer, default=0)
    code = Column(Text, default='')

Base.metadata.create_all(engine)  # 创建所有表结构
