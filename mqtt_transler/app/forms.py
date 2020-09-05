# author:阿豪
# contact: cyhol@qq.com
# datetime:2020/8/15 0015 9:48
# software: PyCharm

"""
文件说明：

"""

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, IntegerField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange

from my_mqtt.mqtt_func import HTTP_FUNC_TYPE


class NoRequiredForm(FlaskForm):
    class Meta:
        def render_field(self, field, render_kw):
            render_kw.setdefault('required', False)
            return super().render_field(field, render_kw)


class SendCommandField(NoRequiredForm):
    cmd_type = SelectField('发送类型', choices=[(k, v[1]) for k, v in HTTP_FUNC_TYPE.items()], default='through')
    # cmd_type = SelectField('发送类型', choices=HTTP_FUNC_TYPE)
    client_id = IntegerField('client_id',
                             validators=[DataRequired(message='请输入设备ID'), NumberRange(message='设备ID为纯数字')],
                             render_kw={'placeholder': '请输入设备ID'})
    func = StringField('function',
                       render_kw={'placeholder': '请输入功能（透传时必填）'})
    payload = StringField('payload', render_kw={'placeholder': '指令内容，没有可以为空'})
    no_check = BooleanField('[不]验证指令是否有效（未录入的新指令需要使用）')
    password = PasswordField('管理员密码')   # , validators=[DataRequired(message='密码必填')])
    submit = SubmitField('发送')

    # password = PasswordField("密码：", validators=[DataRequired("请输入密码")])
    # password2 = PasswordField("确认密码：", validators=[DataRequired("请输入确认密码"), EqualTo("password", "两次密码不一致")])
