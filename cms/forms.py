from attr import fields
from django import forms
from line.models import reserve_inform
#Guide : https://www.learncodewithmike.com/2020/03/django-modelform.html

# class DatetimeInput(forms.DateTimeInput):
#      input_type = "datetime-local"

# class DatetimePickerForm(forms.Form):
#     datetimefield = forms.DateTimeField(widget=DatetimeInput)

class DatetimeModelForm(forms.ModelForm):
    class Meta :
        #表單要綁定的資料模型
        model = reserve_inform
        #指定網頁所要顯示之欄位
        fields = (
            'reserve_name_confirm',
            'reserve_email_confirm',
            'reserve_datetime_confirm',
            )  
        
        #客製化表單屬性
        widgets = {
            'reserve_name_confirm': forms.TextInput(
                attrs={
                    'class'      :'form-control is-valid',
                    'type'       :'text',
                    'id'         :'name',
                    'name'       :'name',
                    'placeholder':'dnaiel chen',
                    'onkeyup'    :'validateName()',
                }
            ),
            'reserve_email_confirm':forms.EmailInput(
                attrs={
                    'class'      :'form-control is-valid',
                    'type'       :'text',
                    'id'         :'email',
                    'name'       :'email',
                    'placeholder':'dnaiel@gmail.com',
                    'onkeyup'    :'validateEmail()',
                }
            ),
            'reserve_datetime_confirm': forms.DateTimeInput(
                attrs={
                    'class' :'form-control is-valid',
                    'type'  :'datetime-local',
                    'id'    :'datetimePicker',
                    'name'  :'datetimePicker',
                    'max'   :'2023-12-30T00:00:00',
                }
            ),
           
        }
        #表單欄位的標題
        labels = {
            'reserve_name_confirm':'姓名:',
            'reserve_email_confirm':'信箱:',
            'reserve_datetime_confirm':'時間:',
        }