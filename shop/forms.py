from django import forms
from shop.models import order_info


class CheckoutModelForm(forms.ModelForm):
    class Meta:
        # 表單要綁定的資料模型
        model = order_info
        # 指定網頁所要顯示之欄位
        fields = (
            'order_name',
            'order_email',
            'order_address',
            'order_item',
            'order_price'
        )
        # 客製化表單屬性
        widgets = {
            'order_name': forms.TextInput(
                attrs={
                    'class': 'w-full px-2 py-2 text-gray-700 bg-gray-200 rounded',
                    'type': 'text',
                    'id': 'cus_name',
                    'name': 'cus_name',
                    'placeholder': 'dnaiel chen',
                    'required': 'required',
                    'aria-label' : 'Name',
                    'onkeyup': 'validateName()',
                }
            ),
            'order_email': forms.TextInput(
                attrs={
                    'class': 'w-full px-2 py-2 text-gray-700 bg-gray-200 rounded',
                    'type': 'text',
                    'id': 'cus_email',
                    'name': 'cus_email',
                    'placeholder': 'daniel@gmail.com',
                    'required': 'required',
                    'aria-label' : 'Email',
                    'onkeyup': 'validateEmail()',
                }
            ),
            'order_address': forms.TextInput(
                attrs={
                    'class': 'w-full px-2 py-2 text-gray-700 bg-gray-200 rounded',
                    'type': 'text',
                    'id': 'cus_address',
                    'name': 'cus_address',
                    'placeholder': 'XX市XX區XX路XX號X樓',
                    'required': 'required',
                    'aria-label' : 'Address',
                    'onkeyup': 'validateAddress()',
                }
            ),
            #供db紀錄用 所以隱藏
            'order_item': forms.HiddenInput(
                attrs={
                    #class auto_filled 自動帶入欄位供db儲存
                    'class': 'auto_filled w-full px-2 py-2 text-gray-700 bg-gray-200 rounded',
                    'type': 'hidden',
                    'id': 'cus_item',
                    'name': 'cus_item',
                    'placeholder': '商品',
                    'aria-label' : 'Item'
                }
            ),
            #供db紀錄用 所以隱藏
            'order_price': forms.HiddenInput(
                attrs={
                    #class auto_filled 自動帶入欄位供db儲存
                    'class': 'auto_filled_price w-full px-2 py-2 text-gray-700 bg-gray-200 rounded',
                    'type': 'hidden',
                    'id': 'cus_price',
                    'name': 'cus_price',
                    'placeholder': '金額',
                    'aria-label' : 'price'
                }
            ),
        }
        # 表單欄位的標題
        labels = {
            'order_name': '姓名 :',
            'order_email': '信箱 :',
            'order_address': '地址 :',
        }
