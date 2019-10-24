from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivymd.theming import ThemeManager
from kivy.uix.screenmanager import ScreenManager,Screen
from kivymd.dialog import MDDialog
from kivymd.label import MDLabel
from kivymd.list import ILeftBody,MDList,TwoLineAvatarIconListItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage
from functools import partial
import urllib.request,urllib.error
import pprint
import json
import time
api='https://www.googleapis.com/books/v1/volumes?q='
url=None
maxres='&maxResults=15'
nextpage='&startIndex='
class BookPhoto(ILeftBody, AsyncImage):
        pass
class ScreenDamager(ScreenManager):
	result=None
	count=None
	page=0
	b_name=''
	def change_screen(self,name):
		self.transition.direction='right'		
		self.current=name
	def next_result(self):
		self.page+=15
		self.search(self.b_name)
	def prev_result(self):
		if self.page==0:
			self.change_screen('screen1')
		else:
			self.page-=15
			self.search(self.b_name,direction='right')
	def search(self,b_name,direction='left'):
		self.b_name=b_name
		url=api+b_name.replace(' ','+')+maxres+nextpage+str(self.page)
		try:
			j=urllib.request.urlopen(url).read()
			result=json.loads(j)
			self.result=result['items']
		except urllib.error.URLError:
			print('Connect to internet')
			MDDialog(title='No Internet',content=MDLabel(text='Please connect to the internet and try again',font_style='Subhead',theme_text_color='Primary'),size_hint=(0.5,0.3)).open()
		except KeyError:
				MDDialog(title='Search unsuccessful',content=MDLabel(text='The book you searched does not seem to appear.',font_style='Subhead',theme_text_color='Primary'),size_hint=(0.5,0.3)).open()
		else:
			self.transition.direction=direction
			self.current='loading'
			self.current='screen2'
			time.sleep(2)	
class Screen1(Screen):
	def search(self,b_name):
		self.manager.search(b_name)
class MyLayout(BoxLayout):
	pass			
class Screen2(Screen):
	def on_pre_enter(self,*args):
		self.clear_widgets()
	def on_enter(self,*args):
		blayout=MyLayout()
		resview=ScrollView()		
		mylist=MDList()
		count=0
		title=authors='Not Available'
		bsrc='Image-not-available.jpg'
		for i in self.parent.result:
			#print('\n'+i+'\n')
			try:title=i['volumeInfo']['title']
			except:pass
			try:authors=i['volumeInfo']['authors']
			except:pass
			try:bsrc=i['volumeInfo']['imageLinks']['smallThumbnail']
			except:pass
			item=TwoLineAvatarIconListItem(text=title,secondary_text=str(authors))
			item.add_widget(BookPhoto(source=bsrc))
			item.bind(on_press=partial(self.change_screen,count))
			mylist.add_widget(item)
			count+=1
		resview.add_widget(mylist)
		blayout.add_widget(resview)
		self.add_widget(blayout)
	def change_screen(self,count,*args):
		print(count)
		self.manager.count=count
		self.manager.transition.direction='left'
		self.manager.current='screen3'
class ReadLayout(BoxLayout):
	pass
class Screen3(Screen):
	def on_pre_enter(self,*args):
		self.clear_widgets()
	def on_enter(self,*args):
		count=self.manager.count
		result=self.manager.result
		title=authors=subtitle=cat=lang=page=pub=amt='Not Available'
		rlayout=ReadLayout()
		blayout=BoxLayout(orientation='horizontal')
		imagesrc='Image-not-available.jpg'

		try:title=result[count]['volumeInfo']['title']
		except:pass
		try:authors=str(result[count]['volumeInfo']['authors'])
		except:pass
		try:imagesrc=result[count]['volumeInfo']['imageLinks']['thumbnail']
		except:pass
		try:pub=result[count]['volumeInfo']['publisher']
		except:pass
		try:lang=result[count]['volumeInfo']['language']	
		except:pass
		try:cat=str(result[count]['volumeInfo']['categories'])		
		except:pass
		try:subtitle=result[count]['volumeInfo']['subtitle']
		except:pass
		try:page=str(result[count]['volumeInfo']['pageCount'])
		except:pass
		try:
			price=result[count]['saleInfo']['listPrice']
			amt=str(price['amount'])+' '+price['currencyCode']
		except:pass
		finally:
			image=AsyncImage(source=imagesrc,size_hint=(0.5,1))
			blayout.add_widget(image)
			grid=GridLayout(cols=2)
			grid.add_widget(BookHead(text='Title:'))
			grid.add_widget(BookLabel(text=title))
			grid.add_widget(BookHead(text='Authors:'))
			grid.add_widget(BookLabel(text=authors))
			grid.add_widget(BookHead(text='Publisher:'))
			grid.add_widget(BookLabel(text=pub))	
			grid.add_widget(BookHead(text='Language:'))
			grid.add_widget(BookLabel(text=lang))
			grid.add_widget(BookHead(text='Categories:'))
			grid.add_widget(BookLabel(text=cat))
			grid.add_widget(BookHead(text='Subtitle:'))
			grid.add_widget(BookLabel(text=subtitle))
			grid.add_widget(BookHead(text='Pagecount:'))
			grid.add_widget(BookLabel(text=page))
			grid.add_widget(BookHead(text='Amount:'))
			grid.add_widget(BookLabel(text=amt))
			blayout.add_widget(grid)
			rlayout.add_widget(blayout)
		self.add_widget(rlayout)

class Loading(Screen):
	pass
class BookHead(MDLabel):
	font_style='Title'
	theme_text_color='Primary'
	size_hint:(0.5,1)
class BookLabel(MDLabel):
	font_style='Subhead'
	theme_text_color='Primary'
class BookApp(App):
    theme_cls = ThemeManager()
    nav_drawer = ObjectProperty()
BookApp().run()
