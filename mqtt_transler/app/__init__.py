# author:阿豪
# contact: cyhol@qq.com
# datetime:2020/8/14 0014 11:10
# software: PyCharm

"""
文件说明：

"""

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from settings import Config


# 创建app应用,__name__是python预定义变量，被设置为使用本模块.
app = Flask(__name__)

# 添加配置信息
app.config.from_object(Config)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

# 如果你使用的IDE，在routes这里会报错，因为我们还没有创建呀，为了一会不要再回来写一遍，因此我先写上了
from app import routes

