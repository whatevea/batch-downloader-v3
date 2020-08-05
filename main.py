from tkinter import *
import os
from tkinter.ttk import *
import tkinter.font as tkFont
import requests
import webbrowser
import vidstream
import vidstream_cdn
import xtream
import mp4upload
import threading
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#this class is made because we cannot passs arguments in callback of button .
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
class Result():
	def __init__(self,json):
		self.title=json['title']
		self.first_ep=(json['detailslink'].split('category/')[1])+"-episode-1"
		self.release_date=json['date']
	def show_btn(self):
		Button(text=self.title,command=self.anime_selected).pack()
	def anime_selected(self):
		show_dl_options(self.first_ep)
#clears the root window 
def clearScreen():
	for item in root.winfo_children():
		item.destroy()
# this is the main screen of app with password  entry box 
def passwordCheck():
	Label(root,text=json['info']).pack()
	Label(root,text="Please Enter the password").pack()
	textentry=Entry(root,width=30)
	textentry.pack()
	submit_button=Button(root,text="Submit",command=lambda:sumbit_password(textentry.get()))
	submit_button.pack()
	show_password=Button(root,text="Dont Know Password",command=open_browser).pack()

# bottom function is called when update is true
def updateRequired():
	Label(root ,text="Update required", font=h1).pack()
	Message(root,text=json['update_reason'],font=h2,width=480,anchor=S).pack()

#this function ensures pastebin data is loaded first 
def loaded():
	global json
	json=eval(requests.get("https://pastebin.com/raw/AxzAmFBi").text)
	lbl.destroy()
	if json['update']:
		updateRequired()
	passwordCheck()

#this opens browser to look for password
def open_browser():
	Label(root,text="If the button doesnt redirects goto https://animesa.ga/pw.html").pack()
	webbrowser.open_new("https://animesa.ga/pw.html")

#this check the password and premium version
def sumbit_password(password):
	if password==json['trial_key']:
		appRender(False)
	elif password==json['premium_key']:
		appRender(True)
	else:
		root.destroy()


#app funtions from here
def appRender(isProParam):
	#the line below clears the widget ROOT 
	clearScreen()
	Label(root ,text="Enter Anime Name", font=h1).pack()
	anime_name=Entry(root,width=30)
	anime_name.pack()
	search_btn=Button(root,text="Search",command=lambda:search(anime_name.get(),search_btn))
	search_btn.pack()
	global isPremium
	isPremium =isProParam

#after search button is pressed
def search(anime_name,search_btn):
	result_frame=Frame(root,width=400)
	result_frame.pack()
	url=f'https://fluted-catalyst-258608.appspot.com/normalsearch?query={anime_name}'
	result_json=requests.get(url).json()
	if len(result_json)==0:
		Label(result_frame,	text="No result found").pack()
	else:
		search_btn.destroy()
		for item in result_json:
			btn=Result(item).show_btn()
#this functions shows the download options like server and episode range 
def show_dl_options(animequery):
	clearScreen()
	Label(font=h2,text=f'Download {animequery.split("-episode")[0]}').pack()
	radio=IntVar()
	radio.set(3) #the first default choice
	Radiobutton(root,text="Mp4upload",variable=radio,value=1).pack()
	Radiobutton(root,text="Xstreamcdn",variable=radio,value=2).pack()
	Radiobutton(root,text="Both",variable=radio,value=3).pack()
	Label(root,text="Starting Episode (must be number)").pack()
	episodeStart=Entry(root,width=30)
	episodeStart.pack()
	Label(root,text="no of episode after Starting episode").pack()
	episode_count=Entry(root,width=30)
	episode_count.pack()
	Button(root,text="Start Download",command=lambda:checkentry(animequery,episodeStart.get(),episode_count.get(),radio.get())).pack()
#check entry and start download
def checkentry(animequery,episodeStart,episode_count,server):
	try:
		episodeStart=int(episodeStart)
		episode_count=int(episode_count)
		if episode_count>json['daily_limit'] and not isPremium:
			Label(root,text=f"you are trial user and cannot download more than {json['daily_limit']}").pack()
		else:
			print("seperate download thread started")
			t1=threading.Thread(target=choose_server,args=[animequery,episodeStart,episode_count,server])
			t1.start()

	except:
		Label(root,text="please enter valid integer").pack()
def choose_server(animequery,episodeStart,episode_count,server):
	clearScreen()
	for i in range(episodeStart,episodeStart+episode_count,1):
		episode=animequery.split('-1')[0]+"-"+str(i)
		print(episode)
		sources=vidstream.vpage(episode).sources
		if isPremium:
			try:
				dlprogress(vidstream_cdn.mp4(vidstream.vpage(episode).id).file()['url'],episode)
			except:
				dlprogress(mp4upload.mp4(sources['Mp4upload']).file()['url'],episode)
		elif server==1:
			dlprogress(mp4upload.mp4(sources['Mp4upload']).file()['url'],episode)
		elif server==2:
			dlprogress(xtream.mp4(sources['Xstreamcdn']).file()['url'],episode)
		elif server==3:
			try:
				dlprogress(mp4upload.mp4(sources['Mp4upload']).file()['url'],episode)
			except:
				dlprogress(xtream.mp4(sources['Xstreamcdn']).file()['url'],episode)
#downloads and show progress	
def dlprogress(url,episode):
	print("downloading from ",url)
	a=1
	Label(root,text=f"Downloading {episode} ").pack()
	r=requests.get(url,stream=True,allow_redirects=True,verify=False)
	f=open(f'{episode}.mp4','wb')
	for ch in r.iter_content(chunk_size=None):
		if ch:
			f.write(ch)
			print(a,"chunks downloaded")
			a=a+1
	f.close()
	Label(root,text=f'Downloaded').pack()
	if not isPremium:
		webbrowser.open_new(json['flood_url'])
#global variables
root=Tk()
h1 = tkFont.Font(family="Lucida Grande", size=30)
h2= tkFont.Font(family="Lucida Grande", size=20)
root.title("AnimeSaga Downloader")
img=PhotoImage(file=resource_path("loading.gif")).subsample(6,6)
lbl=Label(root,image=img)
lbl.pack()
root.geometry("500x500")
root.after(100,loaded)
root.mainloop()
